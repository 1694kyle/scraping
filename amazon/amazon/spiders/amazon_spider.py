from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Spider, Request, Rule, CrawlSpider
from datetime import datetime
from scrapy.selector import Selector
from amazon.items import AmazonItem
import pdb
import re
from amazon.settings import item_file, log_summary_file

def load_xpaths():
    xpaths = {
        'title': './/span[@id="productTitle"]/text()',
        'asin': '',
        'lowest_used_price1': './/a[contains(text(),"Used")]/text()[2]',
        'lowest_new_price1': './/a[contains(text(),"New")]/text()[2]',
        'lowest_used_price2': './/span[a[contains(text(),"Used")]]/span/text()',
        'lowest_new_price2': './/span[a[contains(text(),"New")]]/span/text()',
        'trade_in_eligible': ' ',
        'trade_value': './/span[@id="tradeInButton_tradeInValue"]/text()',
        'url': ' ',
        'price': ' ',
        'profit': ' '
    }
    return xpaths


def build_sub_link(domain_suffix):
    return 'https://www.amazon.com{}'.format(domain_suffix)


class AmazonSpider(CrawlSpider):
    name = 'amazon'
    allowed_domains = [r'www.amazon.com']
    start_urls = [
        r'https://www.amazon.com/Sell-Books/b?node=2205237011',  # node for trade-in
    ]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5})'
    }
    rules = (
        Rule(
            LinkExtractor(allow=('/dp/(\d+)',),),
            callback="parse_item_page"
            ),
        Rule(
            LinkExtractor(allow=('amazon.com/s',),),
            ),
        Rule(
            LinkExtractor(allow=('amazon.com/s',),),
            follow=True
            ),
        )

    def __init__(self, *args, **kwargs):
        super(AmazonSpider, self).__init__(*args, **kwargs)
        self.name = 'amazon'
        self.item_xpaths = load_xpaths()


    def parse_item_page(self, response):
        self.crawler.stats.inc_value('item_count')
        item_count = self.crawler.stats.get_value('item_count')
        self.check_usage()
        sel = Selector(response)
        item = AmazonItem()
        for name, path in self.item_xpaths.iteritems():
            try:
                item[name] = sel.xpath(path).extract()[0].strip().replace(',', '').replace('$', '')
            except (KeyError, IndexError, ValueError):
                item[name] = ' '

        item['url'] = response.url
        item['asin'] = re.search('/dp/(\d+)', response.url).group(1)
        if not item['trade_value'] == ' ':
            item['trade_in_eligible'] = True
        else:
            item['trade_in_eligible'] = False
        with open(item_file, 'a') as f:
            f.write('{} Finished:{} {}\n'.format(item_count, item['asin'], item['title']))

        if not item['title'] == ' ': print '{} Finished:{} {}'.format(item_count, item['asin'], item['title'])

        yield item

    def inc_stat(self, stat):
        self.crawler.stats.inc_value(stat)

    def check_usage(self):
        stats = self.crawler.stats
        request_data = int(stats.get_value('downloader/request_bytes'))
        response_data = int(stats.get_value('downloader/response_bytes'))
        total_used = request_data + response_data

        if total_used > 20000000000:
            with open(log_summary_file, 'w') as f:
                for k, v in stats.__dict__.iteritems():
                    f.write('{}: {}\n'.format(k, v))
            self.crawler.stop()
