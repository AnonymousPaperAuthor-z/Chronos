import scrapy
import json
import time
from spider_module.myfirstSpider.items import Firmware
import spider_module.myfirstSpider.ERT_tool as ERT_tool
# The Reolink website has changed. Previously crawled data is stored in reolink_product_old.json, which will not change anymore. New data and future data will be stored in reolink_product.json
class ReolinkSpider(scrapy.Spider):
    name = "reolink"
    allowed_domains = ['reolink.com']
    time = time.strftime("%Y-%m-%d",time.localtime())

    def parse_data(self, response):
        result = json.loads(response.text)
        firmware_reolink = Firmware()
        for data in result["data"]:
            model = data["title"]
            for each in data["firmwares"]:   
                firmware_reolink["version"] = each["version"].lower().strip()
                updated_at = int(each["updated_at"])//1000
                realse_time = time.strftime("%Y-%m-%d",time.localtime(updated_at))
                # Create item
                firmware_reolink["model"] = model.lower()  
                firmware_reolink["create_time"] = realse_time
                firmware_reolink["crawl_time"] = self.time
                firmware_reolink["name"] = firmware_reolink["model"] + "-" + firmware_reolink["version"]
                if firmware_reolink["create_time"] != "":    
                    firmware_reolink["first_publish_time"] = "null"
                else:
                    firmware_reolink["first_publish_time"] = firmware_reolink["crawl_time"]
                firmware_reolink["source"] = "official website"
                firmware_reolink["ert_time"] = ERT_tool.ERT_generate(firmware_reolink["create_time"], firmware_reolink["first_publish_time"])
                if firmware_reolink["ert_time"] != None:
                    yield firmware_reolink

    def parse_first(self,response):
        result = json.loads(response.text)
        for each in result["data"]:
            dlProductId = each["id"]
            hardwareversions = each["hardwareVersions"]
            for hardwareversion in hardwareversions:
                hardwareVersion = hardwareversion["id"]
                url = "https://reolink.com/wp-json/reo-v2/download/firmware/?dlProductId=" + str(dlProductId) + "&hardwareVersion=" + str(hardwareVersion) + "&lang=en"
                req = scrapy.Request(url, callback= self.parse_data)
                yield req
    def start_requests(self):
        url = "https://reolink.com/wp-json/reo-v2/download/product/selection-list/?lang=en"
        req = scrapy.Request(url, callback=self.parse_first)
        yield req


# def extract_child_list(product_info: dict) -> list:
#     result = [product_info]
#     for child_product in product_info["child"]:
#         result += extract_child_list(child_product)
#     return result




