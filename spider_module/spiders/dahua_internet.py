import scrapy
import json
import re
import time
from spider_module.myfirstSpider.items import Firmware
import spider_module.myfirstSpider.ERT_tool as ERT_tool

class DahuaSpider(scrapy.Spider):
    name = 'dahua_internet'
    pattern = re.compile("DH(?:-[A-Za-z0-9/]+)+")
    allowed_domains = ['www.xiagujian.com/dahuagujian']
    start_urls = ['http://www.xiagujian.com/dahuagujian']
    # start_urls = ['https://supportapi.dahuatech.com/support/api/extend/tools-software/pageFront']
    header = {
            "Host": "supportapi.dahuatech.com"
    }
    proxy = "http://127.0.0.1:8080"
    time = time.strftime("%Y-%m-%d",time.localtime())

    def parse_first(self, response):
        category_ids = set()
        binary_text = response.body
        result = json.loads(binary_text)
        #open("result.html", 'wb').write(binary_text)
        the_package = result["data"][5]["childrenList"]  # Program upgrade package option in Dahua official website  #### The index here may change, need to pay attention to modification
        #self.logger.info(the_package)
        the_package_valid = the_package[:4]
        for type in the_package_valid:
            for series in type["childrenList"]:
                category_ids.add(series["id"]) 
        print(category_ids)
        #print(len(category_ids))
 
        data ={      
            "data": {
                "categoryIds": list(category_ids)
            },
            "pageNo": 1,
            "pageSize": 100
        }
        url = "https://supportapi.dahuatech.com/support/api/extend/tools-software/pageFront"
        body = json.dumps(data)
        post_header = self.header
        post_header["Content-Type"] = "application/json;charset=UTF-8"
        req = scrapy.Request(url, headers=post_header, body=body, method='POST', callback=self.parse)
        yield req
      
    def parse(self,response):
        result = json.loads(response.body)
       #self.logger.info(result["data"]["data"])
        data_dahua = result["data"]["data"]
  
        for product in data_dahua:
            firmware_name = product["title"]
            try:
                index = firmware_name.rindex("V")
            except ValueError:
                continue
            content = product["content"]
            models = self.pattern.findall(content)
            for model in models:
                #instantiate item
                firmware_dahua = Firmware()
                firmware_dahua["model"] = model.lower()
                firmware_dahua["version"] = firmware_name[index:-4].lower()
                firmware_dahua["create_time"] = firmware_dahua["version"][-6:]
                firmware_dahua["first_publish_time"] = product["createTime"]
                firmware_dahua["crawl_time"] = self.time
                firmware_dahua["name"] = firmware_dahua["model"] + "-" + firmware_dahua["version"]
                #update_time = data_dahua["updateTime"] #not sure what this time means yet
                firmware_dahua["source"] = "official website"
                firmware_dahua["ert_time"] = ERT_tool.ERT_generate(firmware_dahua["create_time"], firmware_dahua["first_publish_time"])
                if firmware_dahua["ert_time"] != None:
                    yield firmware_dahua

    def start_requests(self):
        url = "https://supportapi.dahuatech.com/support/api/extend/tools-software/category-front-list"
        # url = "https://support.dahuatech.com/tools/thePackage/"
        # postdata = json.loads('{"data":{"categoryIds":[129,135,146,147,157,158,166,170,181,185,188,192,193,194,196,201,205,209,215,126]},"pageNo":1,"pageSize":10}')
        req = scrapy.FormRequest(url, headers=self.header, method='POST', callback=self.parse_first)
        yield req