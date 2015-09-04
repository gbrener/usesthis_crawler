# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FillableItem(scrapy.Item):
    def fill_empty_fields(self):
        empty_fields = set(self.fields) - set(self)
        for field in empty_fields:
            self[field] = ''


class PersonItem(FillableItem):
    name = scrapy.Field()
    article_url = scrapy.Field()
    pub_date = scrapy.Field()
    title = scrapy.Field()
    img_src = scrapy.Field()
    bio = scrapy.Field()
    hardware = scrapy.Field()
    software = scrapy.Field()
    dream = scrapy.Field()


class ToolItem(FillableItem):
    tool_name = scrapy.Field()
    tool_url = scrapy.Field()
