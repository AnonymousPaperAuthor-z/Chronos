from pandas import Series
import scrapy
import json
import re
import time
from spider_module.myfirstSpider.items import Firmware
import spider_module.myfirstSpider.ERT_tool as ERT_tool

class AvmSpider(scrapy.Spider):
    name = 'avm'
    allowed_domains = ['en.avm.de']
    time = time.strftime("%Y-%m-%d", time.localtime())
    # proxy = "http://127.0.0.1:10891"
    proxy = "http://127.0.0.1:52633"  ### connected to vpn, replace the port to agent port

    def parse_first(self, response):
        serieses = response.xpath('//select[@name="product"]/option/@value').extract()
        for series in serieses[1:]:
            url = "https://en.avm.de/service/update-news/download/product/" + series + "/"
            req = scrapy.Request(url, callback= self.parse, meta={"model":series, "proxy": self.proxy})
            yield req

      
    def parse(self,response):
        
        infoses = response.xpath('//div[@class="meta-infos"]')
        for each_meta in infoses:
            version_flag = each_meta.xpath('.//div[contains(text(),"Version:")]').extract()
            create_time_flag = each_meta.xpath('.//div[contains(text(),"Date:")]').extract()
            # only for version and time both exist
            if len(version_flag) > 0 and len(create_time_flag) > 0:
                each_infos = each_meta.xpath('.//div[@class="row"]')
                for each_info in each_infos:
                    if len(each_info.xpath('.//div[contains(text(),"Version:")]').extract()) > 0:
                        version = each_info.xpath('.//div[2]/text()').extract()[0]
                    # else:
                    #     continue
                    if len(each_info.xpath('.//div[contains(text(),"Date:")]').extract()) > 0:
                        create_time = each_info.xpath('.//div[2]/text()').extract()[0]
                    # else:
                    #     continue
            model = response.meta["model"]
            firmware_avm = Firmware()
            firmware_avm["model"] = model.lower()
            firmware_avm["version"] = version.lower()
            firmware_avm["create_time"] = create_time
            firmware_avm["crawl_time"] = self.time
            firmware_avm["name"] = firmware_avm["model"] + "-" + firmware_avm["version"]
            if firmware_avm["create_time"] != "":
                firmware_avm["first_publish_time"] = "null"
            else:
                firmware_avm["first_publish_time"] = firmware_avm["crawl_time"]
            firmware_avm["source"] = "官网"
            firmware_avm["ert_time"] = ERT_tool.ERT_generate(firmware_avm["create_time"], firmware_avm["first_publish_time"])
            if firmware_avm["ert_time"] != None:
                yield firmware_avm
        

        
    def start_requests(self):
        url = "https://en.avm.de/service/update-news/"
        req = scrapy.Request(url, callback=self.parse_first, meta={"proxy": self.proxy})
        yield req