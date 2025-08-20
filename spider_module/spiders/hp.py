import scrapy
import re
import time
import json
from spider_module.myfirstSpider.items import Firmware
import spider_module.myfirstSpider.ERT_tool as ERT_tool

class HpSpider(scrapy.Spider):  
    name = 'hp'
    pattern_uri = re.compile("var ajaxUrlSDL = '(.*?)';")
    pattern_product = re.compile("https://support.hp.com/my-en/products/(.+)")
    pattern_productNameOid = re.compile("https://support.hp.com/my-en/drivers/selfservice/.*/(\d+)")
    pattern_model = re.compile("https://support.hp.com/my-en/drivers/selfservice/(.*)/(?:\d+)")
    allowed_domains = ['support.hp.com']
    # start_urls = 'https://support.hp.com/wcc-services/prodcategory/my-en/active-products'
    start_urls = ['https://support.hp.com/my-en/products/printers',
                  'https://support.hp.com/my-en/products/scanners-fax/scanners']
    header = {
        "Host": "support.hp.com",
        "Content-Type": "application/json",
    }
    body = {
        "callForRetiredProduct": "false",
        "cc": "my",
        "lc": "en"
    }
    proxy = "http://127.0.0.1:8080"
    # proxy = "http://127.0.0.1:23457"
    time = time.strftime("%Y-%m-%d", time.localtime())

    def get_items(self, response):
        book_mark_url = self.pattern_product.findall(response.url)[0]
        self.body["bookMarkURL"] = book_mark_url
        body = json.dumps(self.body) 
        url = "https://support.hp.com/wcc-services/prodcategory/getProductCategoriesBySeoName"
        req = scrapy.Request(url, method="POST", headers=self.header, body=body, meta={"url": response.url} )
        #req = scrapy.Request(url, method="POST", headers=self.header, body=body, meta={"url": response.url, "proxy": self.proxy} )
        return req

    def parse_1(self, response):
         req = self.get_items(response)
         req.callback = self.parse_first
         yield req
        
    def parse_first(self, response):
        if "printers" in response.meta["url"]:
            uris = get_keywords(response, "seoLabel")
            url_prefix = response.meta["url"]
        elif "scanners" in response.meta["url"]:
            uris = get_keywords(response, "alternateName")
            url_prefix = response.meta["url"]
        for uri in uris:
            url = url_prefix + "/" + uri.lower().replace(" ", "-")
            req = scrapy.Request(url, callback=self.parse_second)
           # req = scrapy.Request(url, callback=self.parse_second, meta={"proxy": self.proxy})
            yield req

    def parse_second(self, response):
        req = self.get_items(response)
        req.callback = self.parse_product_url
        yield req
        

    def parse_product_url(self, response):
        uris = get_keywords(response, "redirectUrl")
        if uris != None:
            if uris[0] == None:
                uris = get_keywords(response, "uid")
                if uris[0] == None:
                    uris = get_keywords(response, "name")
                url_prefix = response.meta["url"]
                for uri in uris:
                    url = url_prefix + "/" + uri
                    req = scrapy.Request(url, callback=self.parse_second)
                    yield req
            else:
                for uri in uris:
                    url = "https://support.hp.com" + uri.replace("/product/", "/drivers/selfservice/")
                    model_information = self.pattern_model.findall(url)[0]
                    req = scrapy.Request(url, callback=self.parse, meta={"model": model_information})
                    # req = scrapy.Request(url, callback=self.parse, meta={"proxy": self.proxy})
                    yield req

    def parse_continue(self, response):
        uris = get_keywords(response, "uid")
        if uris[0] == "null":
            req = scrapy.Request(url, callback=self.parse_continue) 
            yield req
        else:
            for uri in uris:
                url = "https://support.hp.com" + uri.replace("/product/", "/drivers/selfservice/")
                model_information = self.pattern_model.findall(url)[0]
                req = scrapy.Request(url, callback=self.parse, meta={"model": model_information})    
                # req = scrapy.Request(url, callback=self.parse, meta={"proxy": self.proxy})
                yield req

    def parse(self, response):
        base_uri = response.xpath('//html/head/base/@href').extract()[0]
        uri = self.pattern_uri.findall(response.text)[0]
        url = base_uri + uri
        # Construct request
        header = {
        "Host": "support.hp.com",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
        "Cookie": ""
        }
        
        requestJson ={"language":"en","osId":"792898937266030878164166465223921","countryCode":"my","hpTermsOfUseURL":"https://support.hp.com/my-en/document/c00581401","inOSDriverLinkURL":"https://support.hp.com/my-en/document/c01796879","languageValue":"English","bitInfoUrl":"https://support.hp.com/my-en/document/c03666764"}   
        requestJson["productNameOid"] = self.pattern_productNameOid.findall(response.url)[0]
        body = "requestJson=" + json.dumps(requestJson).replace('": "', '":"').replace('", "', '","')
        req = scrapy.Request(url, method="POST", headers=header, body = body, callback=self.parse_firmware, meta={"model": response.meta["model"]})
        yield req

    def parse_firmware(self, response):
        try:
            result = json.loads(response.text)
        except Exception as e:
            print("Error converting response", e)
        else:
            if "swdJson" in result.keys() and result["swdJson"] != None:
                try:
                    result = json.loads(result["swdJson"])
                except Exception as e:
                    print("Error converting swdJson", e)
                else:
                    for each in result:
                        if each["accordianName"] == "Firmware":
                            for firmware in each["softwareDriversList"]:
                                firmware_information = firmware["latestVersionDriver"]   
                                # Initialize item
                                firmware_hp = Firmware()
                                firmware_hp["model"] = response.meta["model"].replace("-series", "").lower()
                                firmware_hp["version"] = firmware_information["version"].lower()
                                firmware_hp["create_time"] = firmware_information["releaseDateString"]    
                                firmware_hp["crawl_time"] = self.time
                                firmware_hp["name"] = firmware_hp["model"] + "-" + firmware_hp["version"]  
                                if firmware_hp["create_time"]!= "":
                                    firmware_hp["first_publish_time"] = "null"
                                else:
                                    firmware_hp["first_publish_time"] = firmware_hp["crawl_time"]
                                firmware_hp["source"] = "official website"
                                firmware_hp["ert_time"] = ERT_tool.ERT_generate(firmware_hp["create_time"], firmware_hp["first_publish_time"])
                                if firmware_hp["ert_time"] != None:
                                    yield firmware_hp 


    def start_requests(self):
        for url in self.start_urls:
            req = scrapy.Request(url, callback=self.parse_1)
           # req = scrapy.Request(url, callback=self.parse_1, meta={"proxy": self.proxy})
            yield req


def get_keywords(response, keyword):
    keywords = []
    if len(response.text) > 0:
        try:
            classes = json.loads(response.text)
        except Exception as e:
            print("Error converting json while searching for keywords:" ,e)
        else:
            field_list = classes["data"]["fieldList"]
            for each in field_list:
                if keyword in each.keys():
                    keywords.append(each[keyword])
                else: 
                    print("Keywords not found")
            return keywords
