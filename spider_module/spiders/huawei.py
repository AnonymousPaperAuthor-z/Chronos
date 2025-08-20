from typing import Pattern
from typing_extensions import ParamSpecArgs
import scrapy
import json
import re
import time
from spider_module.myfirstSpider.items import Firmware
import spider_module.myfirstSpider.ERT_tool as ERT_tool

class HuaweiSpider(scrapy.Spider):
    name = 'huawei'
    pattern = re.compile("o.m0 = '(.*?)'")
    pattern_convert = re.compile("&#x(?:..);")
    allowed_domains = ['support.huawei.com']
    start_urls = ['https://support.huawei.com/enterprise/zh/software/index.html']
    time = time.strftime("%Y-%m-%d",time.localtime())
    proxy = "http://127.0.0.1:8080"

   
    def parse_data(self,response):
        
        result = response.text
        original_text = self.pattern_convert.findall(result)
        for each in original_text:
            result = re.sub(each,chr(int(each[3:5],16)),result)
        data_replace={
            "&quot;":"\"",
            ":null":":\"null\"",
            "true":"\"true\"",
            "false":"\"false\"",
            "\"[":"[",
            "]\"":"]"
        }
        for key in data_replace:
            result = result.replace(key, data_replace[key])
        try:
            result = json.loads(result)
        except:
            print(result)
        else:
            if result != None: # Some resources may be deleted, so there's no information on the webpage
                if "vrList" in result.keys():
                    for each in result["vrList"]:
                        firmware_huawei = Firmware()
                        firmware_huawei["model"] = each["versionOfferingName"].lower().replace("&amp;", "")
                        firmware_huawei["version"] = each["name"].replace(firmware_huawei["model"],"").strip(" ").lower()
                        firmware_huawei["create_time"] = each["issueTime"]
                        firmware_huawei["crawl_time"] = self.time
                        firmware_huawei["name"] = each["name"].lower() # Product name
                        if firmware_huawei["create_time"] != "":      
                            firmware_huawei["first_publish_time"] = "null"
                        else: 
                            firmware_huawei["first_publish_time"] = firmware_huawei["crawl_time"]
                        firmware_huawei["source"] = "official website"
                        firmware_huawei["ert_time"] = ERT_tool.ERT_generate(firmware_huawei["create_time"], firmware_huawei["first_publish_time"])
                        if firmware_huawei["ert_time"] != None:
                            yield firmware_huawei
                else:
                    # This type of data doesn't exist, skip for now
                    pass
            else:
                pass

      
    def parse(self,response):
        if response.xpath('//input[@id="dataNoFoundSoft"]/@value').extract()[0] != "true":
            scripts= response.xpath('//script[contains(text(),"o.m0")]').extract()   
            idAbsPath = self.pattern.search(scripts[0]).group(1)
            subModelOfferingId = response.xpath('//input[@id="subModelOfferingId"]/@value').extract()[0]
            data = "idAbsPath=" + idAbsPath+"&subModelOfferingId="+subModelOfferingId
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Cookie":  "supportelang=zh;"
            }
            url ="https://support.huawei.com/enterpriseproduct/AggregationPageController/selectVersionList"
            req = scrapy.Request(url, method='POST', headers=headers, body=data, callback=self.parse_data)
            yield req
        
    def parse_first(self,response):
        result = response.xpath('//ul[@class="list-name"]')
        for letter in result:
            serieses = letter.xpath('.//li')
            for series in serieses:
                url = series.xpath('.//a/@href').extract()
                url = "https://support.huawei.com" + url[0]
                #self.logger.info(url)
                req = scrapy.Request(url, callback=self.parse)
                yield req

         
    def start_requests(self):
        url = "https://support.huawei.com/enterprise/zh/software/index.html"
        req = scrapy.Request(url, callback=self.parse_first)
        yield req