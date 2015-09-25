# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonItem(scrapy.Item):
    title = scrapy.Field()
    asin = scrapy.Field()
    lowest_used_price1 = scrapy.Field()
    lowest_new_price1 = scrapy.Field()
    lowest_used_price2 = scrapy.Field()
    lowest_new_price2 = scrapy.Field()
    price = scrapy.Field()
    trade_in_eligible = scrapy.Field()
    trade_value = scrapy.Field()
    url = scrapy.Field()
    profit = scrapy.Field()
    roi = scrapy.Field()

