import scrapy
import re
import time
from spider_module.myfirstSpider.items import Firmware
import spider_module.myfirstSpider.ERT_tool as ERT_tool

class MikrotikSpider(scrapy.Spider):
    name = 'mikrotik'
    allowed_domains = ['mikrotik.com']
    start_urls = ['https://mikrotik.com/download/archive']
    proxy = "http://127.0.0.1:8080"
    time = time.strftime("%Y-%m-%d",time.localtime())

      
    def parse(self,response):
        navigations = response.xpath('//li[@class="accordion-navigation"]')
        for each_navigation in navigations:
            version = each_navigation.xpath('.//b/text()').extract()[0].replace("Release ", "")
            release_time = each_navigation.xpath('.//span/text()').extract()[0]
            
            # Initialize item
            firmware_mikrotik = Firmware()
            firmware_mikrotik["model"] = "null"
            firmware_mikrotik["version"] = version.lower()
            firmware_mikrotik["create_time"] = release_time
            firmware_mikrotik["crawl_time"] = self.time
            firmware_mikrotik["name"] = firmware_mikrotik["model"] + "-" + firmware_mikrotik["version"]
            if firmware_mikrotik["create_time"] != "":    
                firmware_mikrotik["first_publish_time"] = "null"
            else:
                firmware_mikrotik["first_publish_time"] = firmware_mikrotik["crawl_time"]
            firmware_mikrotik["source"] = "official website"
            firmware_mikrotik["ert_time"] = ERT_tool.ERT_generate(firmware_mikrotik["create_time"], firmware_mikrotik["first_publish_time"])
            if firmware_mikrotik["ert_time"] != None:
                yield firmware_mikrotik
        

        
    def start_requests(self):
        url = "https://mikrotik.com/download/archive"
        req = scrapy.Request(url, callback=self.parse)
        yield req