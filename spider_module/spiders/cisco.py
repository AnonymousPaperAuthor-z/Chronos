from logging import exception
import scrapy
import json
import re
import time
from spider_module.myfirstSpider.items import Firmware
import spider_module.myfirstSpider.ERT_tool as ERT_tool

class CiscoSpider(scrapy.Spider):
    name = 'cisco'
    allowed_domains = ['cisco.com']
    start_urls = ['https://www.cisco.com/c/en/us/support/all-products.html']
    #pattern = re.compile('(?:.*?)Release Notes for(.*)Release ([0-9.]*)|(?:.*?)Release Notes for(.*) Cisco IOS XE (.*)')
    proxy = "http://127.0.0.1:8080"
    time = time.strftime("%Y-%m-%d",time.localtime())
    #### https://www.cisco.com/c/en/us/support/index.html
  
    def parse_release_notes(self, response):
        if 'nexus-9000-series-switches' in response.url:
            print('nexus-9000-series-switches!!')
        try:
            title = response.xpath('//h1[@id= "fw-pagetitle"]/text()').extract()[0]
        except Exception as e:
            pass
            # print("Cannot find title, please check," + response.url)
            firmware_cisco["source"] = "official website"
        else:
            if 'Release Notes for the Catalyst 3750 and 3750-E Switches, Cisco IOS Release 12.2(55)EY' in title:
                print('Release Notes for the Catalyst 3750 and 3750-E Switches, Cisco IOS Release 12.2(55)EY!!!!')
            if "." in title:
                first_published_time = ""
                first_published_time = response.xpath('//div[@class="updatedDate"]/text()').extract()
                if len(first_published_time) < 1:
                    first_published_time = response.xpath('//div[@id="documentInfo"]/dl/dd/text()').extract()
                final_result = match_model_and_version(title.strip())
                if final_result is not None and len(final_result) == 2:
                    model, version = final_result
                    if len(first_published_time) >= 1:  # 保存带有update信息的
                        firmware_cisco = Firmware()
                        firmware_cisco["model"] = model.replace(",", "").strip().lower()
                        firmware_cisco["version"] = version.strip().lower()
                        print(f"model:{firmware_cisco['model']}, version:{firmware_cisco['version']}")
                        firmware_cisco["crawl_time"] = self.time
                        firmware_cisco["name"] = firmware_cisco["model"] + firmware_cisco["version"] 
                        firmware_cisco["create_time"] = ""
                        if first_published_time != "":
                            firmware_cisco["first_publish_time"] = first_published_time[0].strip()
                        firmware_cisco["source"] = "官网"
                        firmware_cisco["ert_time"] = ERT_tool.ERT_generate(firmware_cisco["create_time"], firmware_cisco["first_publish_time"])
                        if firmware_cisco["ert_time"] != None:
                            yield firmware_cisco
                    release_elements = response.xpath('//p[contains(text(), "Release") and contains(text(), "became available")]')  # 找表格里带有更新信息的
                    for release_element in release_elements:
                        # 获取版本信息
                        release_text = release_element.xpath('text()').get()
                        # version_ = release_text.split(' ')[1]  # 提取版本号
                        # if '.' not in version_:
                        #     version_ = release_text.split(':')[0]
                        version_ = re.findall("Release (.+) became available", release_text)[0]
                        # 获取对应的时间信息
                        time_element = release_element.xpath('../preceding-sibling::td/p[@class="pChart_bodyCMT"]')
                        release_time = time_element.xpath('text()').get()
                        firmware_cisco = Firmware()
                        firmware_cisco["model"] = model.replace(",", "").strip().lower()
                        firmware_cisco["version"] = version_.strip().lower()
                        print(f"model:{firmware_cisco['model']}, version:{firmware_cisco['version']}")
                        firmware_cisco["crawl_time"] = self.time
                        firmware_cisco["name"] = firmware_cisco["model"] + firmware_cisco["version"]
                        firmware_cisco["create_time"] = ""
                        if release_time != "":
                            firmware_cisco["first_publish_time"] = release_time.strip()
                        firmware_cisco["source"] = "official website"
                        firmware_cisco["ert_time"] = ERT_tool.ERT_generate(firmware_cisco["create_time"],
                                                                           firmware_cisco["first_publish_time"])
                        if firmware_cisco["ert_time"] != None:
                            yield firmware_cisco
                else:
                    with open("./error_cisco", "a", encoding="utf-8") as f:
                        print(title, file=f)

    def parse_series(self,response):
        # if 'nexus-9000-series-switches' in response.url:
        #     print('nexus-9000-series-switches')
        # 有显示更多页面的，进入到更多网页中，没有显示更多网页的，则直接取当前的release_notes网址
        if "/products-release-notes-list.html" in response.text and "/products-release-notes-list.html" not in response.url:
            index =response.url.rindex("/") 
            url = response.url[:index] + "/products-release-notes-list.html"
            yield scrapy.Request(url, callback=self.parse_series)

        else:
            # if 'nexus-9000-series-switches' in response.url:
            #     print('nexus-9000-series-switches!')
            urls = response.xpath('//a[contains(text(), "Release Notes for")]/@href').extract()
            urls2 = response.xpath('//a[contains(text(), "Release Notes, Release")]/@href').extract()
            urls = urls + urls2
            if len(urls) > 0:
                for each_url in urls:
                    if "pdf" in each_url:
                        continue
                    if "/products-release-notes-list.html" in each_url:
                        if "http" not in each_url:
                            each_url = "https://www.cisco.com" + each_url
                        yield scrapy.Request(each_url, callback=self.parse_series)
                    else:
                        if "http" not in each_url:
                            each_url = "https://www.cisco.com" + each_url
                        yield scrapy.Request(each_url, callback=self.parse_release_notes)
            

        
    def parse_index(self,response):
        request_list = list()
        # 非标准页面，所有根据特殊的链接方式找到进入所有产品的网页链接
        if ("All Supported Analytics and Automation Software Products" in response.text) \
            or ("All Supported Data Center Analytics Products" in response.text) \
            or ("All Supported Hyperconverged Infrastructure Products" in response.text)\
            or ("All Supported Jabber Products" in response.text) \
            or ("All Cisco Service Exchange products are beyond the End-of-Support Date and are no longer supported." in response.text) \
            or ("All Cisco Services Support" in response.text) \
            or ("Cisco Business" in response.text) \
            or ("All Supported Cisco ONE Software Releases" in response.text) \
            or ("All Supported WebEx Products" in response.text):
            href_elements = response.xpath('//a[starts-with(@href, "//www.cisco.com/c/en/us/support/")]')
            for href in href_elements:

                if len(href.xpath('./a/@href').extract()) > 0:
                    request_list.append(href.xpath('./a/@href').extract()[0])
        # 标准页面，根据数字以及字母表排所有的产品系列
        else:
            uri_serieses_number = response.xpath('//ul[@id="prodByNumber"]/li/p/span/a/@href').extract()
            uri_serieses_alpha = response.xpath('//ul[@id="prodByAlpha"]/li/a/@href').extract()
            uri_serieses = uri_serieses_number + uri_serieses_alpha  ### 合并列表
            for uri in uri_serieses:
                request_list.append("https://www.cisco.com" + uri)
        # 手动增加url
        add_url_list = ['https://www.cisco.com/c/en/us/support/switches/catalyst-3750-series-switches/products-release-notes-list.html',
                        'https://www.cisco.com/c/en/us/support/switches/catalyst-4500-series-switches/products-release-notes-list.html',
                        'https://www.cisco.com/c/en/us/support/unified-communications/small-business-voice-gateways-ata/series.html',
                        'https://www.cisco.com/c/en/us/support/collaboration-endpoints/unified-ip-phone-8800-series/products-release-notes-list.html',
                        'https://www.cisco.com/c/en/us/support/collaboration-endpoints/unified-ip-phone-7800-series/series.html',
                        'https://www.cisco.com/c/en/us/support/routers/small-business-rv-series-routers/products-release-notes-list.html',
                        'https://www.cisco.com/c/en/us/support/routers/small-business-rv-series-routers/products-release-notes-list.html#anchor14']
        request_list += add_url_list
        for url in request_list:
            req = scrapy.Request(url, callback=self.parse_series) #进入每个系列的页面
            #print("[parse_index:113] 请求：" + url)
            yield req

    # 获取每个系列的网页url
    def parse_category(self, response):
        uri_products_tds = response.xpath('//*[@id="productCategories"]/div/table/tbody/tr/td')
        for uri_products_td in uri_products_tds:
            uri_products = uri_products_td.xpath('.//ul/li/a/@href').extract()
            for uri in uri_products:
                url = "https:" + uri
                req = scrapy.Request(url, callback=self.parse_index)
                yield req

    # 进入所有产品的分系列的网页    
    def start_requests(self):
        url = "https://www.cisco.com/c/en/us/support/all-products.html"
        req = scrapy.Request(url, callback=self.parse_category)
        yield req

def match_model_and_version(title: str) -> tuple:
    result = []
    if re.findall("^Release Notes for (.*)(?=, (Release|Cisco IOS X|IOS X))(.*)$", title):
        # 有逗号的话要匹配到最后一个逗号
        result = re.findall("^Release Notes for (.*)(?=, (?:Release|Cisco IOS X|IOS X))(?:[^0-9]*)(.*)$", title)
    elif re.findall("\d+\.[^ ]+(?: -)?(?: +)?Release Notes for ", title):
        # Release Notes for出现在中间的情况, 版本在前面的情况, Release前面可能包含一个 “ - ", 需要匹配掉, Release前面的空格数量也不确定
        result = re.findall("[^0-9]+(.*)(?: -)?(?: +)?Release Notes for (.*)", title)
        result = [(result[0][1], result[0][0])]
    elif re.findall(" Release Notes for ", title):
        # Release Notes for出现在中间的情况
        if title.startswith("Cisco IOS"):
            result = re.findall("(?:.+) Release Notes for (.*)(?=, )(?:.*)(?=\d+\.)(.*)", title)
        else:
            result = re.findall("(.+) Release Notes for (?:.*)(?=\d+\.)(.*)", title)
    elif re.findall("^Release Notes for (.+)(?=for Cisco IOS Release|Release|Firmware|for Cisco IOS|for Cisco Wireless)(.*)", title):
        # 出现了上述关键词的情况
        result = re.findall("^Release Notes for (?:the )?(.+)(?=for Cisco IOS Release|Release|Firmware|for Cisco IOS|for Cisco Wireless)(?:[^0-9]*)(.*)", title)
    ###0604
    elif re.findall("Release Notes, Release", title):
        result = re.findall("(.+) Release Notes, Release (.+)", title)
    else:
        # 其他情况，前面的型号信息匹配到数字结束
        result = re.findall("^Release Notes for (?:the )?(.+)(?= [0-9])(.*)", title)
    return result[0]

    