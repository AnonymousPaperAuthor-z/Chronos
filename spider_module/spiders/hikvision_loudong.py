from unittest import result
import scrapy
import json
import re
import time
from spider_module.myfirstSpider.items import Firmware
import spider_module.myfirstSpider.ERT_tool as ERT_tool

class HikvisionSpider(scrapy.Spider):
    name = 'hikvision_loudong'   
    allowed_domains = ['www.hikvision.com']
    time = time.strftime("%Y-%m-%d",time.localtime())

    def parse(self, response):
        trs = response.xpath("//table/tbody")
        if len(trs) >= 2:
            data = trs[1]
            row_list = data.xpath('./tr')  
            start_col = 0
            end_col = -1
            if "序号" in row_list[0].xpath('./td[1]/text()').extract():
                row_list = row_list[1:]
                start_col = 1
            if "下载链接" in row_list[0].xpath('./td[1]/text()').extract():
                end_col = -2

            current_affect_version = ""
            data_list = []
            for each_row in row_list:    
                tds = each_row.xpath('./td')
                if len(tds) > start_col + 2:
                    current_affect_version = tds[start_col + 1]
                data_list.append([tds[start_col], current_affect_version, tds[end_col]])
            # Process each row of data
            Firmware_hikvision = Firmware()
            for each_data in data_list:
                models = each_data[0].xpath('.//text()').extract()
                models = "".join(models)
                if "、" in models:
                    models = models.split("、")
                elif "\n" in models:
                    models = models.split("\n")
                else:
                    models = models.split(" ")
                for model in models:
                    if model != "":
                        model = model.strip("系列")
                        infected_versions = each_data[1].xpath('.//text()').extract()
                        infected_versions = "".join(infected_versions)
                        if "V" in infected_versions:
                            if "-" in infected_versions:
                                infected_versions = infected_versions.split("-")
                                for infected_version in infected_versions:
                                    infected_version = infected_version.strip()
                                    Firmware_hikvision["model"] = model.strip().replace("x","*").lower() # Convert matching character x to * as required and change to lowercase
                                    Firmware_hikvision["version"] = infected_version.lower()
                                    Firmware_hikvision["name"] = Firmware_hikvision["model"] + "-" +Firmware_hikvision["version"]
                                    infected_version = infected_version.replace("Build", "build")
                                    if "build" in infected_version:
                                        Firmware_hikvision["create_time"] = infected_version.split("build")[1].strip()
                                    else :
                                        Firmware_hikvision["create_time"] = "null"
                                    Firmware_hikvision["first_publish_time"] = Firmware_hikvision["create_time"]
                                    Firmware_hikvision["crawl_time"] = self.time
                                    Firmware_hikvision["source"] = "vulnerability report"  
                                    Firmware_hikvision["ert_time"] = ERT_tool.ERT_generate(Firmware_hikvision["create_time"], Firmware_hikvision["first_publish_time"])       
                                    if Firmware_hikvision["ert_time"] != None:
                                        yield Firmware_hikvision

                        
                        fix_version = each_data[-1].xpath('.//text()').extract()
                        if "点击下载" in fix_version:
                            pass
                        else:
                            fix_version = fix_version[0]
                            fix_version = fix_version.strip()
                            Firmware_hikvision["model"] = model.strip().replace("x","*").lower()
                            Firmware_hikvision["version"] = fix_version.lower()
                            Firmware_hikvision["name"] = Firmware_hikvision["model"] + "-" + Firmware_hikvision["version"]
                            fix_version = fix_version.replace("Build", "build")
                            if "build" in fix_version:
                                Firmware_hikvision["create_time"] = fix_version.split("build")[1].strip()
                            else :
                                Firmware_hikvision["create_time"] = "null"
                            Firmware_hikvision["first_publish_time"] = Firmware_hikvision["create_time"]
                            Firmware_hikvision["crawl_time"] = self.time
                            Firmware_hikvision["source"] = "vulnerability report"  
                            Firmware_hikvision["ert_time"] = ERT_tool.ERT_generate(Firmware_hikvision["create_time"], Firmware_hikvision["first_publish_time"])       
                            if Firmware_hikvision["ert_time"] != None:
                                yield Firmware_hikvision
           
    def parse_first(self,response):
        result = json.loads(response.text)
        dataArray = result["content"]["data"]["dataArray"]
        for each_data in dataArray:
            if "漏洞" in each_data["title"]:
                uri = each_data["newsUrl"]
                url = "https://www.hikvision.com" + uri
                yield scrapy.Request(url, callback=self.parse)
              
              
    def start_requests(self):
        url = "https://www.hikvision.com/content/hikvision/cn/support/CybersecurityCenter/SecurityNotices/jcr:content/root/responsivegrid/article_listing_copy.download-pages.json"
        yield scrapy.Request(url, callback=self.parse_first)