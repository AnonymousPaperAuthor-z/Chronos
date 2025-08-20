import scrapy
from scrapy import Selector, Request

from selenium import webdriver
from selenium.webdriver.common.by import By
from scrapy.cmdline import execute
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
# sys.path.append('D:\\iie\\scrapy_project\\general')
from spider_module.myfirstSpider.items import GeneralItem
from spider_module.myfirstSpider.items import Firmware
import time
import spider_module.myfirstSpider.ERT_tool as ERT_tool

class AxisOsSpider(scrapy.Spider):
    name = 'axis_os'
    allowed_domains = []
    start_urls = ['https://help.axis.com/']
    time = time.strftime("%Y-%m-%d", time.localtime())

    def parse(self, response, **kwargs):
        browser = webdriver.Chrome()
        # browser.get(kwargs['product_url'])
        # browser.get('https://software.cisco.com/download/home/286322137/type/282046477/release/Dublin-17.12.1?i=!pp')
        browser.get('https://help.axis.com/en-us/axis-os-release-notes#release-notes-about')
        browser.maximize_window()
        WebDriverWait(browser, 20, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/main/div/div/div/div[1]/div/div[3]/div/div/div/a/span')))
        sections = browser.find_elements(By.XPATH, '//*[@class="col"]/section')
        track_dict = {}
        track = ''
        for section in sections:
            if 'Go to Products on ' in section.text:
                track = section.text.split('\n')[0]
                track_dict[track] = {"version_info": {}, "model_list": []}
            if section.text.startswith('AXIS OS ') and 'Release date' in section.text:
                version = section.text.split('\n')[0].replace('AXIS OS ', '')
                release_date = section.text.split('\n')[1].replace('Release date: ', '')
                track_dict[track]["version_info"][version] = release_date
            if section.text.startswith('Products on '):
                track = section.text.split('\n')[0].replace('Products on ', '')
                for model in section.text.split('\n')[1:]:
                    if model.startswith('The') or model.startswith('From'):
                        continue
                    else:
                        model_list = []
                        if '/' in model:
                            model_body = []
                            # head
                            model_1 = model.split('/')[0]
                            model_head = model_1.split('-')[0]
                            if '-' in model_1:
                                model_body.append(model_1.split('-')[1])
                            else:
                                model_body.append(' ')
                            body_list = model.split('-')
                            # tail
                            if ' ' in body_list[-1]:
                                model_body.append(body_list[-1].split(' ')[0])
                                model_last = body_list[-1].replace(body_list[-1].split(' ')[0], '')
                            else:
                                model_body.append(body_list[-1])
                                model_last = ''
                            for body in body_list[1:-1]:
                                model_body.append(body.replace('/', '').strip())
                            for body in model_body:
                                if body != ' ':
                                    add_model = model_head + '-' + body + model_last
                                else:
                                    add_model = model_head + model_last
                                model_list.append(add_model)
                        else:
                            model_list.append(model)
                        # tail
                        try:
                            track_dict[track]["model_list"] += model_list
                        except KeyError:
                            track = section.text.split('\n')[0].split(' - ')[-1]
                            track_dict[track]["model_list"] += model_list

        browser.get('https://help.axis.com/en-us/axis-os-release-notes-archive#axis-os-11')
        browser.maximize_window()
        WebDriverWait(browser, 20, 0.5).until(EC.visibility_of_element_located(
            (By.XPATH, '//*[@id="app"]/div/main/div/div/div/div[1]/div/div[3]/div/div/div/a/span')))
        sections = browser.find_elements(By.XPATH, '//*[@class="col"]/section')
        track = ''
        for section in sections:
            if 'In this section' in section.text:
                track = section.text.split('\n')[0]
                track_dict[track] = {"version_info": {}, "model_list": []}
                if track == 'AXIS OS 11':
                    track_dict[track]["model_list"] = track_dict["LTS 2024 - 11.11"]["model_list"]
                if track == 'AXIS OS 10':
                    track_dict[track]["model_list"] = track_dict["LTS 2022 - 10.12"]["model_list"]
                if track == 'LTS 2020 (9.80) archive':
                    track_dict[track]["model_list"] = track_dict["LTS 2020 - 9.80"]["model_list"]
                if track == 'LTS 2018 (8.40) archive':
                    track_dict[track]["model_list"] = track_dict["PSS 8.40"]["model_list"]
                if track == 'LTS 2016 (6.50) archive':
                    track_dict[track]["model_list"] = track_dict["PSS 6.50"]["model_list"]
                if track == 'AXIS OS 9 to 5':
                    track_dict[track]["model_list"] = track_dict["PSS 6.50"]["model_list"] + track_dict["PSS 8.40"]["model_list"] + track_dict["LTS 2020 - 9.80"]["model_list"]

            add_list = ['LTS 2018 - 8.40.2']
            if 'Release date' in section.text or section.text.split('\n')[0] in add_list:
                if section.text.startswith('AXIS OS '):
                    version = section.text.split('\n')[0].replace('AXIS OS ', '')
                    release_date = section.text.split('\n')[1].replace('Release date: ', '')
                    track_dict[track]["version_info"][version] = release_date
                if section.text.startswith('Active '):
                    version = section.text.split('\n')[0].lower()
                    release_date = section.text.split('\n')[1].replace('Release date: ', '')
                    track_dict[track]["version_info"][version] = release_date
                if section.text.startswith('LTS '):
                    version = section.text.split('\n')[0].split(' - ')[-1]
                    release_date = section.text.split('\n')[1].replace('Release date: ', '')
                    track_dict[track]["version_info"][version] = release_date
                if section.text.split('\n')[0] == 'LTS 2018 - 8.40.2':
                    version = section.text.split('\n')[0].split(' - ')[-1]
                    release_date = '2019-03-18'
                    track_dict[track]["version_info"][version] = release_date
        axis_item = Firmware()
        for track, info in track_dict.items():
            axis_item['track'] = track
            if track == "LTS 2020 (9.80) archive":
                print('binggo')
            for model in info["model_list"]:
                axis_item['model'] = model.lower().replace('axis', '').strip()
                for version, release in info["version_info"].items():
                    axis_item['version'] = version
                    axis_item['crawl_time'] = time.strftime("%Y-%m-%d",time.localtime())
                    axis_item['create_time'] = ''
                    axis_item['source'] = '官网 release note'
                    if len(release.split('(')) == 2:
                        # axis_item['create_time'] = # three weak later?
                        release = release.split('(')[0]

                    if len(release.split(' – ')) == 2 or len(release.split(' - ')) == 2 or len(release.split(' — ')) == 2 or len(release.split(' -')) == 2 or len(release.split(' –')) == 2:
                        date_list = release.split(' – ')
                        if len(date_list) != 2:
                            date_list = release.split(' - ')
                        if len(date_list) != 2:
                            date_list = release.split(' — ')
                        if len(date_list) != 2:
                            date_list = release.split(' -')
                        if len(date_list) != 2:
                            date_list = release.split(' –')
                        for i, date in enumerate(date_list):
                            axis_item['version'] = axis_item['version'] + '_' + str(i)
                            axis_item["first_publish_time"] = date.strip()
                            axis_item["first_publish_time"] = axis_item["first_publish_time"].replace('–', '-').strip()
                            axis_item["ert_time"] = ERT_tool.ERT_generate(axis_item["create_time"],
                                                                          axis_item["first_publish_time"])
                            axis_item['name'] = '-'.join(
                                [axis_item['model'], axis_item['version'], axis_item["ert_time"]])
                            yield axis_item
                    else:
                        axis_item["first_publish_time"] = release
                        axis_item["first_publish_time"] = axis_item["first_publish_time"].replace('–', '-').strip()
                        axis_item["ert_time"] = ERT_tool.ERT_generate(axis_item["create_time"], axis_item["first_publish_time"])
                        axis_item['name'] = '-'.join(
                            [axis_item['model'], axis_item['version'], axis_item["ert_time"]])

                        yield axis_item


            

# execute(['scrapy', 'crawl', 'cisco_3850'])
