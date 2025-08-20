import scrapy
import json
import re
import time
from spider_module.myfirstSpider.items import Firmware
import spider_module.myfirstSpider.ERT_tool as ERT_tool
# Hikvision international website

class HikvisionSpider(scrapy.Spider):
    name = 'hikvision_en'
    allowed_domains = ['www.hikvision.com']
    start_urls = ['https://www.hikvision.com/en/support/download/firmware/']
    time = time.strftime("%Y-%m-%d",time.localtime())
    proxy = "http://127.0.0.1:8080"
       
    def parse(self,response):
        result = response.xpath('//div[@class="main-item"]')
        
        for each in result:
            models = each.xpath('.//div[@class="sub-section"]/ul/li/text()').extract()
            versions = each.xpath('.//div[@class="firmware-section"]/ul/li/a/text()').extract()
            for model in models:
                for version in versions:
                    firmware_hikvision = Firmware()
                    firmware_hikvision["model"] = model.strip().lower()
                    firmware_hikvision["version"] = version.replace("Firmware_","").lower()
                    if firmware_hikvision["version"][-6:].isdigit():
                        firmware_hikvision["create_time"] = firmware_hikvision["version"][-6:]
                    else:
                        firmware_hikvision["create_time"] = "null"
                    firmware_hikvision["crawl_time"] = self.time
                    firmware_hikvision["name"] = firmware_hikvision["model"] + "-" + firmware_hikvision["version"]
                    if firmware_hikvision["create_time"] != "":   
                        firmware_hikvision["first_publish_time"] = "null"
                    else:
                        firmware_hikvision["first_publish_time"] = firmware_hikvision["crawl_time"]    
                    firmware_hikvision["source"] = "international website"    
                    firmware_hikvision["ert_time"] = ERT_tool.ERT_generate(firmware_hikvision["create_time"], firmware_hikvision["first_publish_time"])       
                    if firmware_hikvision["ert_time"] != None:
                        yield firmware_hikvision
        

            
            
       
           
    def start_requests(self):
        url = "https://www.hikvision.com/en/support/download/firmware/"
        req = scrapy.Request(url, callback=self.parse)
        yield req