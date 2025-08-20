import scrapy
import re
import time
from spider_module.myfirstSpider.items import Firmware
import spider_module.myfirstSpider.ERT_tool as ERT_tool

class UniviewSpider(scrapy.Spider):
    name = 'uniview'
    pattern_models = re.compile("软件适用于以下产品型号：<br>(.*?)<br>")
    pattern_version = re.compile("版本号：(.*?)<br>")
    allowed_domains = ['cn.uniview.com']
    # start_urls = ['https://cn.uniview.com/Service/Service_Training/Download/Tools/']
    start_urls = ['https://cn.uniview.com/Service/Service_Training/Download/Client/']
    # proxy = "http://127.0.0.1:8080"
    proxy = "http://127.0.0.1:23457"
    time = time.strftime("%Y-%m-%d",time.localtime())

    def parse_first(self, response):
        serieses = response.xpath('//div[@class="fztools"]/ul/li')
        for series in serieses:
            uri = series.xpath('.//a/@href').extract()[0]
            url = "https://cn.uniview.com" + uri
            req = scrapy.Request(url, callback= self.parse)
            yield req

      
    def parse(self,response):
        tables = response.xpath('//div[@class="fztools"]/table')
        for each_table in tables:
            information = each_table.xpath('.//tbody/tr[2]/td').extract()[0]

            version = self.pattern_version.search(information).group(1)
            models_list = self.pattern_models.search(information).group(1).split("、")
            for model in models_list:
                # Initialize item
                firmware_uniview = Firmware()
                firmware_uniview["model"] = model.lower()
                firmware_uniview["version"] = version.lower() 
                firmware_uniview["create_time"] = version[-6:] # Firmware release time is the last six digits of the version number
                firmware_uniview["crawl_time"] = self.time
                firmware_uniview["name"] = firmware_uniview["model"] + "-" + firmware_uniview["version"]
                if firmware_uniview["create_time"] != "":    
                    firmware_uniview["first_publish_time"] = "null"
                else:
                    firmware_uniview["first_publish_time"] = firmware_uniview["crawl_time"]
                firmware_uniview["source"] = "official website"
                firmware_uniview["ert_time"] = ERT_tool.ERT_generate(firmware_uniview["create_time"], firmware_uniview["first_publish_time"])
                if firmware_uniview["ert_time"] != None:
                    yield firmware_uniview

    def start_requests(self):
        # url = "https://cn.uniview.com/Service/Service_Training/Download/Tools/"
        url = "https://cn.uniview.com/Service/Service_Training/Download/Client/"
        req = scrapy.Request(url, callback=self.parse_first)
        yield req