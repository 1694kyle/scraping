# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
import csv
from amazon import settings


def write_to_csv(item):
    writer = csv.writer(open(settings.csv_file_path, 'a'), lineterminator='\n')
    writer.writerow([item['asin'], item['title'], item['price'], item['trade_value'], item['profit'], item['roi'], item['url']])# [item[key] for key in item.keys()])


class WriteToCsv(object):
    def process_item(self, item, spider):
        write_to_csv(item)
        return item


class TradeEligiblePipeline(object):

    def process_item(self, item, spider):
        if not item['trade_in_eligible']:
            raise DropItem('Not Trade Eligible: {}'.format(item['asin']))
        elif item['trade_value'] == ' ':
            raise DropItem('\tNot Trade Value: {}'.format(item['asin']))
        else:
            return item


class HasUsedPipeline(object):

    def process_item(self, item, spider):
        if item['lowest_used_price1'] == ' ' and item['lowest_used_price2'] == ' ':
            raise DropItem('\tNo Used: {}'.format(item['asin']))
        else:
            prices = ['lowest_used_price1', 'lowest_used_price2', 'lowest_new_price1', 'lowest_new_price2']
            price_values = []
            for price in prices:
                try:
                    price_values.append(float(item[price]))
                except:
                    continue  # no price for price key
            min_price = min(price_values)
            item['price'] = min_price
            return item


class ProfitablePipeline(object):

    def process_item(self, item, spider):
        price = item['price']
        trade_value = float(item['trade_value'])

        if trade_value - price > 10:
            item['roi'] = '%{}'.format(round((trade_value - price) / price * 100, 2))
            item['profit'] = '${}'.format(trade_value - price)
            print '\tProfit Found: {}'.format(item['profit'])
            return item
        else:
            raise DropItem('\tNot Profitable: {}'.format(item['asin']))


class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['asin'] in self.ids_seen:
            raise DropItem("\tDuplicate item found: {}".format(item['asin']))
        elif item['title'] == ' ':
            raise DropItem('\tNo Title Found: {}'.format(item['asin']))
        else:
            self.ids_seen.add(item['asin'])
            return item
