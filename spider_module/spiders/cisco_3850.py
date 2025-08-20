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

class Ciso3850Spider(scrapy.Spider):
    name = 'cisco_3850'
    allowed_domains = []
    start_urls = ['http://www.cisco.com/']
    time = time.strftime("%Y-%m-%d", time.localtime())

    # def parse(self, response):
    #     browser = webdriver.Chrome()
    #     browser.maximize_window()
    #     browser.get('https://www.cisco.com/c/en/us/support/switches/catalyst-9500-series-switches/series.html#~tab-downloads')
    #     WebDriverWait(browser, 20, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="seriesDownloadSelector"]/ul/li[1]/button')))
    #     buttons = browser.find_elements(By.XPATH, '//*[@id="seriesDownloadSelector"]/ul/li/button')[1:]
    #     menu_button = browser.find_element(By.XPATH, '//*[@id="seriesDownloadSelector"]/ul/li[1]/button')
    #     product_urls = []
    #     for button in buttons: 
    #         button.click()
    #         time.sleep(2)
    #         try:
    #             WebDriverWait(browser, 20, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//th[text() = "Smart Switch Firmware" or text() = "Smart Plus Switch Firmware" or text() = "Switch Firmware" or text() = "Industrial Ethernet Software" or text() = "ME Ethernet Access Software" or text() = "IOS Software" or text() = "NX-OS System Software" or text() = "IOS XE Software" or text() = "Cisco Network Assistant"]/../following-sibling::tr/td/a[text() = "All Releases"][1]')))
    #         except:
    #             menu_button.click()
    #             continue
    #         sel = Selector(text= browser.page_source)
    #         menu_button.click()
    #         time.sleep(1)
    #         product_urls.append(sel.xpath('//th[text() = "IOS Software"]/../following-sibling::tr/td/a[text() = "All Releases"]/@href').extract_first())
    #         product_urls.append(sel.xpath('//th[text() = "Smart Switch Firmware"]/../following-sibling::tr/td/a[text() = "All Releases"]/@href').extract_first())
    #         product_urls.append(sel.xpath('//th[text() = "Smart Plus Switch Firmware"]/../following-sibling::tr/td/a[text() = "All Releases"]/@href').extract_first())
    #         product_urls.append(sel.xpath('//th[text() = "Switch Firmware"]/../following-sibling::tr/td/a[text() = "All Releases"]/@href').extract_first())
    #         product_urls.append(sel.xpath('//th[text() = "Industrial Ethernet Software"]/../following-sibling::tr/td/a[text() = "All Releases"]/@href').extract_first())
    #         product_urls.append(sel.xpath('//th[text() = "ME Ethernet Access Software"]/../following-sibling::tr/td/a[text() = "All Releases"]/@href').extract_first())
    #         product_urls.append(sel.xpath('//th[text() = "NX-OS System Software"]/../following-sibling::tr/td/a[text() = "All Releases"]/@href').extract_first())
    #         product_urls.append(sel.xpath('//th[text() = "IOS XE Software"]/../following-sibling::tr/td/a[text() = "All Releases"]/@href').extract_first())
    #         product_urls.append(sel.xpath('//th[text() = "Cisco Network Assistant"]/../following-sibling::tr/td/a[text() = "All Releases"]/@href').extract_first())

    #     product_urls = [item for item in product_urls if item is not None]
    #     for product_url in product_urls:
    #         yield Request(url = product_url, callback= self.product_proc, cb_kwargs={'product_url':product_url},dont_filter=True)
        

    def parse(self, response, **kwargs):
        browser = webdriver.Chrome()
        # browser.get(kwargs['product_url'])
        # browser.get('https://software.cisco.com/download/home/286322137/type/282046477/release/Dublin-17.12.1?i=!pp')
        browser.get('https://software.cisco.com/download/home/286324992/type/286325166/release/7.5.1')
        browser.maximize_window()
        WebDriverWait(browser, 20, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="release-details-expandall-button"]')))
        expand_all_button = browser.find_element(By.XPATH, '//*[@id="release-details-expandall-button"]') 
        expand_all_button.click()
        versions = browser.find_elements(By.XPATH, '//tree-node-children//div[@class="flex-center-container"]/span')
        version_sum = len(versions)
        for version_num in range(version_sum):
            try:
                versions = browser.find_elements(By.XPATH, '//tree-node-children//div[@class="flex-center-container"]/span')
                version = versions[version_num]
                first_url = browser.current_url
                browser.execute_script("arguments[0].click();", version)
                WebDriverWait(browser, 20, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//div[@header="image-table-date-header"]')))
                second_url = browser.current_url
                if second_url != first_url:
                    sel = Selector(text = browser.page_source)
                    date_sum = sel.xpath('//div[@header="image-table-date-header"]')
                    for date_num in range(len(date_sum)):
                        cisco_3850_item = Firmware()
                        cisco_3850_item['model'] = sel.xpath(
                            '//*[@id="release-product-title"]/text()').extract_first()
                        if cisco_3850_item['model'] in ['2901 Integrated Services Router', '2911 Integrated Services Router', '2921 Integrated Services Router', '2951 Integrated Services Router']:
                            cisco_3850_item['model'] = 'c2900@' + cisco_3850_item['model']
                        if cisco_3850_item['model'] in ['3925 Integrated Services Router', '3945E Integrated Services Router', '3925E Integrated Services Router', '3945 Integrated Services Router']:
                            cisco_3850_item['model'] = 'c3900@' + cisco_3850_item['model']
                        if cisco_3850_item['model'] in ['1921 Integrated Services Router', '1941 Integrated Services Router', '1981 Integrated Services Router', '1905 Serial Integrated Services Router']:
                            cisco_3850_item['model'] = 'c1900@' + cisco_3850_item['model']
                        if cisco_3850_item['model'] in ['SF220-24 24-Port 10/100 Smart Switch', 'SF220-24P 24-Port 10/100 PoE Smart Switch', 'SF220-48 48-Port 10/100 Smart Switch', 'SF220-48P 48-Port 10/100 PoE Smart Switch', 'SG220-26 26-Port Gigabit Smart Switch', 'SG220-26P 26-Port Gigabit PoE Smart Switch', 'SG220-28 28-Port Gigabit Smart Switch', 'SG220-28MP 28-Port Gigabit PoE Smart Switch', 'SG220-50 50-Port Gigabit Smart Switch', 'SG220-50P 50-Port Gigabit PoE Smart Switch', 'SG220-52 52-Port Gigabit Smart Switch']:
                            cisco_3850_item['model'] = 'c220@' + cisco_3850_item['model']

                        cisco_3850_item['version'] = version.text
                        if len(cisco_3850_item['version']) < 3:
                            continue
                        cisco_3850_item["crawl_time"] = self.time
                        cisco_3850_item["name"] = cisco_3850_item["model"] + cisco_3850_item["version"]
                        cisco_3850_item["create_time"] = ""

                        cisco_3850_item["first_publish_time"] = sel.xpath('//div[@header="image-table-date-header"]')[date_num].xpath('text()').extract_first().strip()
                        cisco_3850_item["ert_time"] = ERT_tool.ERT_generate(cisco_3850_item["create_time"],
                                                                           cisco_3850_item["first_publish_time"])
                        # cisco_3850_item['file_name'] = sel.xpath('//span[@class="pointer text-darkgreen"]')[date_num].xpath('text()').extract_first()
                        yield cisco_3850_item
                else:
                    WebDriverWait(browser, 20, 0.5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="release-details-expandall-button"]')))
                    expand_all_button = browser.find_element(By.XPATH, '//*[@id="release-details-expandall-button"]')
                    browser.execute_script("arguments[0].click();", expand_all_button)
                    sel = Selector(text = browser.page_source)
                    date_sum = sel.xpath('//div[@header="image-table-date-header"]')
                    for date_num in range(len(date_sum)):
                        cisco_3850_item = Firmware()

                        cisco_3850_item['model'] = sel.xpath('//*[@id="release-product-title"]/text()').extract_first()
                        if cisco_3850_item['model'] in ['2901 Integrated Services Router', '2911 Integrated Services Router', '2921 Integrated Services Router', '2951 Integrated Services Router']:
                            cisco_3850_item['model'] = 'c2900@' + cisco_3850_item['model']
                        if cisco_3850_item['model'] in ['3925 Integrated Services Router', '3945E Integrated Services Router', '3925E Integrated Services Router', '3945 Integrated Services Router']:
                            cisco_3850_item['model'] = 'c3900@' + cisco_3850_item['model']
                        if cisco_3850_item['model'] in ['1921 Integrated Services Router', '1941 Integrated Services Router', '1981 Integrated Services Router', '1905 Serial Integrated Services Router']:
                            cisco_3850_item['model'] = 'c1900@' + cisco_3850_item['model']
                        if cisco_3850_item['model'] in ['SF220-24 24-Port 10/100 Smart Switch', 'SF220-24P 24-Port 10/100 PoE Smart Switch', 'SF220-48 48-Port 10/100 Smart Switch', 'SF220-48P 48-Port 10/100 PoE Smart Switch', 'SG220-26 26-Port Gigabit Smart Switch', 'SG220-26P 26-Port Gigabit PoE Smart Switch', 'SG220-28 28-Port Gigabit Smart Switch', 'SG220-28MP 28-Port Gigabit PoE Smart Switch', 'SG220-50 50-Port Gigabit Smart Switch', 'SG220-50P 50-Port Gigabit PoE Smart Switch', 'SG220-52 52-Port Gigabit Smart Switch']:
                            cisco_3850_item['model'] = 'c220@' + cisco_3850_item['model']
                        cisco_3850_item['version'] = version.text
                        if len(cisco_3850_item['version']) < 3:
                            continue
                        cisco_3850_item["crawl_time"] = self.time
                        cisco_3850_item["name"] = cisco_3850_item["model"] + cisco_3850_item["version"]
                        cisco_3850_item["create_time"] = ""
                        cisco_3850_item['first_publish_time'] = sel.xpath('//div[@header="image-table-date-header"]')[
                            date_num].xpath('text()').extract_first().strip()
                        cisco_3850_item["ert_time"] = ERT_tool.ERT_generate(cisco_3850_item["create_time"],
                                                                            cisco_3850_item["first_publish_time"])

                        # cisco_3850_item['file_name'] = sel.xpath('//span[@class="pointer text-darkgreen"]')[date_num].xpath('text()').extract_first()
                        yield cisco_3850_item
            except:
                continue

            

# execute(['scrapy', 'crawl', 'cisco_3850'])
