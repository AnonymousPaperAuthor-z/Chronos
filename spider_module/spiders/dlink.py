from base64 import encode
import scrapy
import re
import time
import json
from spider_module.myfirstSpider.items import Firmware
import spider_module.myfirstSpider.ERT_tool as ERT_tool
import random

class DlinkSpider(scrapy.Spider):
    name = 'dlink'
    pattern_model = re.compile("[(/]?([a-zA-Z]+-[a-zA-Z0-9]+(?:\(\w+\))?)")
    pattern_version = re.compile("\(([a-zA-Z0-9_\-. ]+?(?:\([a-zA-Z0-9_\-. ]+?\))?(?:[a-zA-Z0-9_\-. ]+?)?)\)")    #pattern_version = re.compile("(?:[^a-zA-Z0-9]{2,}|otfix |ote |\.\d{2} )\(([a-zA-Z0-9_\-. ]+?(?:\([a-zA-Z0-9_\-. ]+?\))?(?:[a-zA-Z0-9_\-. ]+?)?)\)")
    #pattern_version = re.compile("\(([^一-龥]+)\)")
    #pattern_version = re.compile(".*[一-龥P][一-龥()\sMIB]+(?:.*?)\((.*)\)")
    allowed_domains = ['www.dlinktw.com.tw']
    proxy = "http://127.0.0.1:8080"
    time = time.strftime("%Y-%m-%d",time.localtime())

## todo:https://support.dlink.com/resource/products/

    def parse(self, response):
        """

        """
        try:
            if "\\u9AD4" in response.text:  ### "體" (tǐ) 件
                result = json.loads(response.text)
                if "item" in result.keys():
                    items = result["item"]
                    #
                    choosed_items = choose(items)  ### Choose items containing firmware
                    for item in choosed_items:
                        files = item["file"]
                        #
                        for file in files:
                            name = file["name"]
                            model = self.pattern_model.findall(name)
                            if len(model) > 0:
                                break
                        assert len(model) > 0

                        #
                        for file in files:
                            name = file["name"]
                            if "體" in name:
                                version = self.pattern_version.findall(name)
                                assert len(version) > 0
                                first_publish_time = file["date"]
                                id = file["id"]
                                #
                                url = "https://www.dlinktw.com.tw/techsupport/ShowFileDescrip.aspx?id=" + str(id)
                                req = scrapy.Request(url, callback= self.parse_firmware, meta={"model":model[0], "version": version[-1], "first_publish_time": first_publish_time})
                                yield req  ### Generate request

        except Exception as e:
            print(e, "no model or version found,", name, response.url)

    def parse_firmware(self, response):
        result = response.text
        if "體日期" in result:
            date_information = self.pattern_date.findall(result)
            if len(date_information) > 0:
                first_publish_time = date_information[0].replace("\u5e74", "/").replace("\u6708", "/") # Replace year and month with / to standardize date format
            else:
                print("no publication time,", response.url)
                first_publish_time = response.meta["first_publish_time"]
        else:
            # If no date in file description, use the date shown on official website
            first_publish_time = response.meta["first_publish_time"]
        # Initialize item
        firmware_dlink = Firmware()
        firmware_dlink["model"] = response.meta["model"].lower()
        firmware_dlink["version"] = response.meta["version"].lower()
        firmware_dlink["create_time"] = ""
        firmware_dlink["crawl_time"] = self.time
        firmware_dlink["name"] = firmware_dlink["model"] + "-" + firmware_dlink["version"]
        firmware_dlink["first_publish_time"] = first_publish_time
        firmware_dlink["source"] = "official website"
        firmware_dlink["ert_time"] = ERT_tool.ERT_generate(firmware_dlink["create_time"], firmware_dlink["first_publish_time"])
        if firmware_dlink["ert_time"] != None:
            yield firmware_dlink

    # def start_requests(self):
    #     for ver in range(1,816):
    #         url = "https://www.dlinktw.com.tw/techsupport/ajax/ajax.ashx?action=productfile&ver=" + str(ver)
    #         req = scrapy.Request(url, callback=self.parse)
    #         yield req

    def start_requests(self):  ### 修改 加入随机数循环
        index_list = []
        for i in range(5000):
            random_index = random.random()
            index_list.append(10 * random_index)
            index_list.append(100 * random_index)
            index_list.append(1000 * random_index)
        for ver in index_list:
            random_index = random.random()
            url = "https://www.dlinktw.com.tw/techsupport/ajax/ajax.ashx?action=productfile&ver=" + str(ver)
            req = scrapy.Request(url, callback=self.parse)
            yield req


def choose(items):
    # choosed_items = [] 
    # for item in items:
    #     if "體" in json.dumps(item, ensure_ascii=False):
    #         choosed_items.append(item) 
    # return choosed_items
    return [item for item in items if "體" in json.dumps(item, ensure_ascii=False)]
