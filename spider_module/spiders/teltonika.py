from ensurepip import version
import scrapy
import re
import time
from spider_module.myfirstSpider.items import Firmware
import spider_module.myfirstSpider.ERT_tool as ERT_tool

class TeltonikaSpider(scrapy.Spider):
    name = 'teltonika'
    allowed_domains = ['wiki.teltonika-networks.com']
    start_urls = 'https://wiki.teltonika-networks.com/view/Main_Page'
    proxy = "http://127.0.0.1:8080"
    time = time.strftime("%Y-%m-%d",time.localtime())

    def parse_index(self, response):
        device_types = response.xpath('//table[@class="main-table w-100"]/tbody/tr[1]/td')
        for device_type in device_types[:4]: # Only take the first four device types, the remaining device types have no firmware, can be adjusted according to the actual situation of the official website
            trs = device_type.xpath('.//table/tbody/tr')
            for tr in trs[3:]: # Data starts from the fourth row of the table
                model = tr.xpath('.//td/a/text()').extract()
                if len(model) > 0:
                    uri = tr.xpath('.//td/a/@href').extract()[0]
                    url = "https://wiki.teltonika-networks.com" + uri +"_Firmware_Downloads" # Since it was found that each model's firmware download page is just the model name + firmware_downloads, so in this step directly jump to each model's firmware download page
                    req = scrapy.Request(url, callback= self.into_history, meta={"model": model[0]})
                    yield req

    def into_history(self,response):
        uri_history = response.xpath('//li[@id="ca-history"]/span/a/@href').extract()[0]
        url = "https://wiki.teltonika-networks.com" + uri_history
        req = scrapy.Request(url, callback= self.parse_history, meta={"model": response.meta["model"]})
        yield req

    def parse_history(self,response):
        uri_firmwares = response.xpath('//a[@class="mw-changeslist-date"]/@href').extract()
        for uri_firmware in uri_firmwares:
            url = "https://wiki.teltonika-networks.com" + uri_firmware
            req = scrapy.Request(url, callback= self.parse_firmware, meta={"model": response.meta["model"]})
            yield req

    def parse_firmware(self,response):
        package_name = ""
        first_publish_time = ""
        if "This page contains various firmware" in response.text:
            try:
                package_name = response.xpath('//*[@id="mw-content-text"]/div/table/tbody/tr[2]/td[2]/b/a/text()').extract()[0] 
                first_publish_time = response.xpath('//*[@id="mw-content-text"]/div/table/tbody/tr[2]/td[3]/b/a/text()').extract()[0]
            except Exception as e:
                print(e)
        if "This page contains firmware files" in response.text:       
            try:
                # package_name = response.xpath('//*[@id="mw-content-text"]/div/div/table/tbody/tr[2]/td[1]/a/text()').extract()[0]
                package_name = response.xpath('//*[@id="mw-content-text"]/div/div/table/tbody/tr[2]/td[1]/span/a/text()' ).extract()[0]
                # first_publish_time = response.xpath('//*[@id="mw-content-text"]/div/div/table/tbody/tr[2]/td[3]/text()').extract()[0]
                first_publish_time = response.xpath('//*[@id="mw-content-text"]/div/div/table/tbody/tr[2]/td[3]/text()').extract()[0]
            except Exception as e:
                package_name_abnormal = response.xpath('//*[@id="mw-content-text"]/div/div/table/tbody/tr[2]/td[1]/text()').extract()[0]
                if package_name_abnormal == "[[Media:{{{latest_fw}}}_WEBUI.bin|{{{latest_fw}}}]]" or package_name_abnormal == "[[Media:_WEBUI.bin|]]":
                    # These data have issues with the webpage itself, for example https://wiki.teltonika-networks.com/wikibase/index.php?title=RUT951_Firmware_Downloads&oldid=87772
                    pass # Skip this case, it's an error in the webpage itself
                else:
                    print("Failed to get package name, package name is: " + package_name_abnormal + " URL is: " + response.url)
        if package_name != "": # Got a normal package name
            # Process package name to get version
            try:
                index_R = package_name.rindex("R") # The version is after the last R in the package name
            except Exception as e: 
                print("Could not find R in package name, package name is: " + package_name + " URL is: " + response.url)
            else:
                version = package_name[index_R+2:]
                # Initialize item
                firmware_teltonika = Firmware()
                firmware_teltonika["model"] = response.meta["model"].lower()
                firmware_teltonika["version"] = version.lower().replace("_webui.bin", "")
                firmware_teltonika["create_time"] = "null"
                firmware_teltonika["crawl_time"] = self.time
                firmware_teltonika["name"] = firmware_teltonika["model"] + "_" + firmware_teltonika["version"]
                firmware_teltonika["first_publish_time"] = first_publish_time # Sometimes the format of this time is written incorrectly on the website, in which case the ERT conversion will fail, and this data will be skipped directly.
                firmware_teltonika["source"] = "official website"
                firmware_teltonika["ert_time"] = ERT_tool.ERT_generate(firmware_teltonika["create_time"], firmware_teltonika["first_publish_time"])
                if firmware_teltonika["ert_time"] != None:
                    yield firmware_teltonika
                    
    def start_requests(self):
        req = scrapy.Request(self.start_urls, callback=self.parse_index)
        yield req