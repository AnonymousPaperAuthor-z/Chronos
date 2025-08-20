import os
from base64 import encode
import scrapy
import re
import time
import json
from spider_module.myfirstSpider.items import Firmware
import spider_module.myfirstSpider.ERT_tool as ERT_tool
import random
import pdfplumber
import tempfile

class AxisSpider(scrapy.Spider):
    name = 'axis'
    pattern_model = re.compile("[(/]?([a-zA-Z]+-[a-zA-Z0-9]+(?:\(\w+\))?)")
    pattern_version = re.compile("\(([a-zA-Z0-9_\-. ]+?(?:\([a-zA-Z0-9_\-. ]+?\))?(?:[a-zA-Z0-9_\-. ]+?)?)\)")
    pattern_date = re.compile("(20[0-9]{1,2}[^0-9]{1,2}[0-9]{1,2}[^0-9]{1,2}[0-9]{1,2})")
    allowed_domains = ['www.axis.com']
    proxy = "http://127.0.0.1:8080"
    time = time.strftime("%Y-%m-%d",time.localtime())
    url_restore_list = []

    def start_requests(self):
        url = "https://www.axis.com/ftp/pub/axis/software/"
        req = scrapy.Request(url, callback=self.parse_product)
        yield req

    def parse_product(self, response):
        uri_products = response.xpath('.//tr/td/a/@href').extract() # extract urls of each class
        for uri in uri_products:
            #
            if uri in ['MPQT/', 'PACS/']:
                url = response.url + uri
                req = scrapy.Request(url, callback=self.parse_product_details)
                yield req

    def parse_product_details(self, response):
        url_list = response.xpath('.//tr/td/a/@href').extract()
        for url in url_list[1:]:
            if '/' in url:
                url_next = response.url + url
                req = scrapy.Request(url_next, callback=self.parse_product_details)
                yield req
            elif 'release_note' or 'RELEASENOTE' in url:
                self.url_restore_list.append(url)
                url_next = response.url + url
                req = scrapy.Request(url_next, callback=self.parse_pdf, meta={'url': url_next})
                yield req

    def parse_pdf(self, response):
        print(response.url)
        model_list = []
        pdf_data = response.body
        model = response.url.split('/')[-1].split('_')[0].lower()
        model_list.append(model)
        # tmp file
        result_1 = []
        result_1_f = []
        result_1_d = []
        if '.txt' in response.url.lower():
            # print('txt')

            pdf_data = response.body.decode('utf-8')
            # text_line = pdf_data.split('\r\n')
            # for line in text_line:
            # result_version = re.findall("Firmware:*\s*([^\s\n]+)", pdf_data)
            affect_product = re.findall("Products affected:*\s*([^\r\n]+)", pdf_data)
            result_version = re.findall("Firmware version:*\s*([^\r\n]+)", pdf_data)
            result_date = re.findall("Release date:*\s*(?=.*\d)(.+)\n", pdf_data)
            tmp = affect_product[0].lower()
            if 'axis' in tmp:
                tmp = tmp.replace('axis', '').strip()
            if tmp not in model_list:
                model_list.append(affect_product)

        # else:  # delete==True means tmp file will be deleted when closed
        #     print("url error, please check：", response.url)

            firmware_dlink = Firmware()
            for model_ in model_list:
                firmware_dlink["model"] = model_.lower()
                firmware_dlink["version"] = result_version[0].lower()
                firmware_dlink["create_time"] = ""
                firmware_dlink["crawl_time"] = self.time
                firmware_dlink["name"] = firmware_dlink["model"] + "-" + firmware_dlink["version"]
                firmware_dlink["first_publish_time"] = result_date[0].strip()
                if ':' in firmware_dlink["first_publish_time"]:
                    firmware_dlink["first_publish_time"] = firmware_dlink["first_publish_time"].split(':')[-1].strip()
                firmware_dlink["source"] = "官网"
                firmware_dlink["ert_time"] = ERT_tool.ERT_generate(firmware_dlink["create_time"],
                                                                   firmware_dlink["first_publish_time"])
                if firmware_dlink["ert_time"] != None:
                    print(f'{firmware_dlink["model"]}---{firmware_dlink["version"]}---{firmware_dlink["ert_time"]}')
                    yield firmware_dlink


                        # print(text)
        # print("///")


if __name__ == '__main__':
    url = "https://support.dlink.com/resource/products/DWL-8610AP/REVA/DWL-8610AP_REVA_RELEASE_NOTES_4.3.0.6_EN.pdf"



