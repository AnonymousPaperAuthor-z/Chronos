import scrapy
import re, json
import time
from spider_module.myfirstSpider.items import Firmware
import spider_module.myfirstSpider.ERT_tool as ERT_tool


class ZyxelSpider(scrapy.Spider):
    name = 'zyxel'
    allowed_domains = ['portal.myzyxel.com']
    start_urls = ['https://portal.myzyxel.com/my/firmwares']  # Registration required
    # proxy = "http://127.0.0.1:8080"
    proxy = "http://127.0.0.1:23457"
    time = time.strftime("%Y-%m-%d", time.localtime())
    ### Cookie and x_csrf_token need to be updated for each crawl
    ##### Request path: https://portal.myzyxel.com/my/firmwares/datatable.json
    cookie = "zp_locale=en; time_zone=Asia/Shanghai; _ga=GA1.3.1008887991.1687251545; back_url=https%3A%2F%2Fportal.myzyxel.com%2F; _gid=GA1.3.1542526477.1725096240; _gat_UA-65334227-4=1; _ga_V9NL90BHX4=GS1.3.1725096240.7.0.1725096240.0.0.0; _zyxel_portal_session=ZE51eE9MZ0kwV2VRQ2U5NFNkb1pZYmIwWHZGRmw0ajZvYlNhWmZXcitEV0gyMzNGeWN6WnFZZ0xiQjAzWVYra2ZqNk85ZndqWFlWSmpCb1gvTXdGOGNFR0VESnBjdEoyaTVxaUU0VUlnelFsbjU1YWpVbUVXcmFvM1k4aGl4L3dTMjhieDBQRTgyNVhTcEYraUVUcVlYdUdtRzhtd09mTlNXWWRjSkZ6bXVHR2k4cFhTVU1BbGVNa2MwU1pCRFhncExWMDVtR1R4NkQrWjhNN0dLa1UvUnFuZWtoYVk4TmJQV1R4QTNSWXFJYllvNjVKNjl1YjBpekhqQ2QxWDJFeGN5Q2JvS254dEhpVTRwWkpxMzcrMS9tTEtkNDFLVG9JZW9aVUprMEYrSGJLZXVJRGRDNjdpZlRXSVFDLzBjamlHTnZTbTFFVFlISFBuT0wvcVFRSmVoOStIWTdWQnZnWkZ1RnJicGVXMjFoWmZhMmlDRTJHZElZRU9GTXNMT2ZDdEJHTmU1LzdPTy9KZWU2d201RC9WZHZFOWhjZkxTeTVCOTVYTS9EaC8wRXJnWUpscCsvZWxZRDVyOE5TYmRBQ0ZMK0FSSDFpNGpZVkJDaW9HM2ZTd2tZK3MwRnJqd2I1ZjAyaVJRWjk5L0lkNm5STG94VEdlRW1jWTJkTUkvK3lhMzc1T2prUU40S1d5cWFJTVNWbGNxeU5MSURiaFlZblJtN2l3OHl3by9ZSU04eGVyRGFCRHpLMlFKM3VKRHBtNDhmWSs4MEFwek9FWEtUeGpsMWFFZWErc1pmV1lWUHBoaVF6TXEzNVJGRXZka21lWWxjaWduMS9GaXRmVyszWEZjRFIyRUJldTcweWtsUGkyaTI2S1I4RmVKRUZsdzlxelBBTUR5SWFFcDhCWjhjOTNuZTNlc3FUdEw0dUk2QWpNbGJUOWJPemhRMFREd0JLNXVQRFcwRkN3d2Z4WTJUOHhkUDlPTGFxekl2a3NlTnUzY3EvRHdwRnRITXFZVTVxQmhpUEFmQzFxMlU3SWp3YkdGcmxTQT09LS1wL2l6a0JGOEtrbmwwZGQyWVNSQnlBPT0%3D--5813cfd86e2bfc6f4378beab6e2d00c6676b5467"
    x_csrf_token = "AULPI7QA8qIFg3xEnTIIQf5EHUSl2ZeranEHEgZBErD0VQyfh7wbecwPXxXo74ymHoovZy1AIYF5tzqSBeRKiA=="
    def parse_model(self, response):
        models = response.xpath('//*[@id="model"]/option/text()').extract()
        for model in models[1:]:
            url = "https://portal.myzyxel.com/my/firmwares.js?model=" + model
            header = {
                "Host": "portal.myzyxel.com",
                "X-Requested-With": "XMLHttpRequest",
                "Cookie": self.cookie}
            req = scrapy.Request(url, headers=header, callback=self.parse_version, meta={"model": model})
            yield req

    def parse_version(self, response):
        versions = re.findall("<option value=\\\\\"(.*?)\\\\", response.text)
        for version in versions:
            url = "https://portal.myzyxel.com/my/firmwares/datatable.json"
            body = {
                "model": response.meta["model"],
                "fw_version": version
            }
            header = {
                "Host": "portal.myzyxel.com",
                ### X-CSRF-Token needs to be updated for each crawl
                "X-CSRF-Token": self.x_csrf_token,
                "Cookie": self.cookie
            }
            req = scrapy.FormRequest(url, method='POST', headers=header, formdata=body, callback=self.parse_firmware,
                                     meta={'model': response.meta["model"], 'version': version})
            yield req

    def parse_firmware(self, response):
        data = response.text
        release_time = re.findall("\\\\u003e(.*?)\\\\u003c/span\\\\u003e", data)[0]
        
        firmware_zyxel = Firmware()
        firmware_zyxel["model"] = response.meta['model'].lower()
        firmware_zyxel["version"] = response.meta['version'].lower()
        firmware_zyxel["create_time"] = release_time
        firmware_zyxel["crawl_time"] = self.time
        firmware_zyxel["name"] = firmware_zyxel["model"] + "-" + firmware_zyxel["version"]
        if firmware_zyxel["create_time"] != "":
            firmware_zyxel["first_publish_time"] = "null"
        else:
            firmware_zyxel["first_publish_time"] = firmware_zyxel["crawl_time"]
        firmware_zyxel["source"] = "official website"
        firmware_zyxel["ert_time"] = ERT_tool.ERT_generate(firmware_zyxel["create_time"],
                                                           firmware_zyxel["first_publish_time"])
        if firmware_zyxel["ert_time"] != None:
            yield firmware_zyxel

    def start_requests(self):
        url = "https://portal.myzyxel.com/my/firmwares"
        header = {
            "Cookie": self.cookie
        }
        req = scrapy.Request(url, headers=header, callback=self.parse_model)
        yield req
