from numpy import product
import scrapy
import re
import time
from spider_module.myfirstSpider.items import Firmware
import spider_module.myfirstSpider.ERT_tool as ERT_tool

class SynologySpider(scrapy.Spider):
    name = 'synology_download_center'
    pattern_version = re.compile("/download/Os/(.*)$")
    allowed_domains = ['www.synology.cn']
    start_urls = 'https://www.synology.cn/zh-cn/support/download/'
    proxy = "http://127.0.0.1:8080"
    time = time.strftime("%Y-%m-%d",time.localtime())

    def parse_first(self, response):
        serieses = response.xpath('//*[@id="select2-whe1-results"]')
        for series in serieses[1:]:
            uri = series.xpath('.//th/a/@href').extract()[0]
            url = "https://archive.synology.cn" + uri
            req = scrapy.Request(url, callback= self.parse_second)
            yield req

    def parse_second(self, response):
        serieses = response.xpath('/html/body/main/div[2]/table/tbody/tr')
        for series in serieses[1:]:
            uri = series.xpath('.//th/a/@href').extract()[0]
            url = "https://archive.synology.cn" + uri
            req = scrapy.Request(url, callback= self.parse)
            yield req
      
    def parse(self,response):

        version_information = response.xpath('//html/head/title/text()').extract()[0]
        version = self.pattern_version.search(version_information).group(1).replace("/","-")
       
        products = response.xpath('//html/body/main/div[2]/table/tbody/tr')
        for each_product in products[1:]:
            package_name = each_product.xpath('.//th/a/text()').extract()[0]
            if "synology" in package_name:
                index = package_name.rindex("_")
                model = package_name[index+1:].replace(".pat", "")
                model = model.upper()
                if model[:2].isdigit():
                    model = "DS" + model
            else:
                if "_" in package_name:
                    first_underline = package_name.find("_")
                    second_underline = package_name[first_underline+1:].find("_")
                    if second_underline == -1:
                        model = package_name[:first_underline]
                    else:
                        model = package_name[first_underline+1:first_underline+1+second_underline]
            create_time = each_product.xpath('.//td[1]/text()').extract()[0]
            firmware_synology = Firmware()
            firmware_synology["model"] = model.lower()
            firmware_synology["version"] = version.lower()
            firmware_synology["create_time"] = create_time
            firmware_synology["crawl_time"] = self.time
            firmware_synology["name"] = firmware_synology["model"] + "-" + firmware_synology["version"]
            if firmware_synology["create_time"] != "":    
                firmware_synology["first_publish_time"] = "null"
            else:
                firmware_synology["first_publish_time"] = firmware_synology["crawl_time"]
            firmware_synology["source"] = "官网"
            firmware_synology["ert_time"] = ERT_tool.ERT_generate(firmware_synology["create_time"], firmware_synology["first_publish_time"])
            if firmware_synology["ert_time"] != None:
                yield firmware_synology
        
    def start_requests(self):
        req = scrapy.Request(self.start_urls, callback=self.parse_first)
        yield req