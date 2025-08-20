# Spider for Hikvision China official website
# Only crawl data with build date
# Version numbers can be seen in downloads, but models cannot be distinguished, so only crawl direct data from official website pages

import scrapy
import json
import re
import time
from spider_module.myfirstSpider.items import Firmware
import spider_module.myfirstSpider.ERT_tool as ERT_tool

class HikvisionSpider(scrapy.Spider):
    name = 'hikvision_cn'
    allowed_domains = ['www.hikvision.com']
    start_urls = 'https://www.hikvision.com/content/hikvision/cn/support/Downloads/Device-upgrade-package/jcr:content/root/responsivegrid/article_listing_copy.download-pages.json'
    time = time.strftime("%Y-%m-%d",time.localtime())
    proxy = "http://127.0.0.1:8080"
    pattern_model = re.compile('程序包适用于以下型号：(.*)')
    pattern_version = re.compile('版本号：(.*)')
       
    def parse(self,response):
        result = json.loads(response.text)
        for data in result["content"]["data"]["dataArray"]:
            if "VR" in data["title"] or "网络摄像机升级程序包" in data["title"]:
                url = "https://www.hikvision.com" + data["newsUrl"]
                req = scrapy.Request(url, callback= self.parse_data)
                yield req

    def parse_data(self, response):
   
        divs = response.xpath('//div[@class="cmp-text"]')
        for div in divs:
            information = div.xpath('.//p/text()').extract()
            models = ""
            for each in information:
                if "型号" in each:
                    try:
                        models = self.pattern_model.findall(each)[0].strip()
                    except Exception as e:
                        print("Failed to match model with regex, " + each)
                elif "版本" in each:
                    try:
                        version = self.pattern_version.findall(each)[0].strip()
                    except Exception as e:
                        print("Failed to match version with regex, " + each)
            if models != "":
                models = models.split("、")
                for model in models:               
                    firmware_hikvision = Firmware()
                    firmware_hikvision["model"] = model.replace("\u00a0","").replace("\uff08", "(").replace("\uff09", ")").lower() # Manually convert unicode encoding for model and version
                    firmware_hikvision["version"] = version.replace("\u00a0","").lower()
                    if firmware_hikvision["version"][-6:].isdigit():
                        firmware_hikvision["create_time"] = firmware_hikvision["version"][-6:]
                    else:
                        print("Check time format")
                        firmware_hikvision["create_time"] = "null"
                    firmware_hikvision["crawl_time"] = self.time
                    firmware_hikvision["name"] = firmware_hikvision["model"] + "-" + firmware_hikvision["version"]
                    if firmware_hikvision["create_time"] != "":   
                        firmware_hikvision["first_publish_time"] = "null"
                    else:
                        firmware_hikvision["first_publish_time"] = firmware_hikvision["crawl_time"]       
                    firmware_hikvision["source"] = "China official website"    
                    firmware_hikvision["ert_time"] = ERT_tool.ERT_generate(firmware_hikvision["create_time"], firmware_hikvision["first_publish_time"])     
                    if firmware_hikvision["ert_time"] != None:
                        yield firmware_hikvision
        

            
            
       
           
    def start_requests(self):
        req = scrapy.Request(self.start_urls, callback=self.parse)
        yield req