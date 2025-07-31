# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Firmware(scrapy.Item):
    # define the fields for your item here like:
    track = scrapy.Field()
    model = scrapy.Field()
    version = scrapy.Field()
    create_time = scrapy.Field()
    first_publish_time = scrapy.Field()
    crawl_time = scrapy.Field()
    name = scrapy.Field()
    source = scrapy.Field()
    ert_time = scrapy.Field()


# def to_string(self):
# return "{" + ", ".join('"' + field_name + '": "' + self[field_name] + '"' for field_name in self.fields.keys()) + "}"
# return "{\"model\": \"" + self["model"] + "\", \"version\": \"" + self["version"] + "\", \"create_time\": \"" + self["create_time"] + "\", \"first_publish_time\": \"" + self["first_publish_time"] + "\"}"

class FileItem(scrapy.Item):
    file_urls = scrapy.Field()
    files = scrapy.Field()
    model = scrapy.Field()
    create_time = scrapy.Field()


class GeneralItem(scrapy.Item):
    # define the fields for your item here like:
    # brand = scrapy.Field()
    # product_class = scrapy.Field()
    # product_type = scrapy.Field()
    # product_name = scrapy.Field()
    # product_description = scrapy.Field()
    # product_url = scrapy.Field()
    # crawl_time = scrapy.Field()
    # name = scrapy.Field()
    product_name = scrapy.Field()
    product_version = scrapy.Field()
    product_date = scrapy.Field()
    file_name = scrapy.Field()

def add_item_fields(item, product_name, product_description, product_type, product_url):
    item['product_name'] = product_name
    item['product_description'] = product_description
    item['product_type'] = product_type
    item['product_url'] = product_url