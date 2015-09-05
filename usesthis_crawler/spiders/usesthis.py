# -*- coding: utf-8 -*-

import urlparse
import scrapy
import re
from usesthis_crawler.items import PersonItem, ToolItem
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Join, TakeFirst, Identity
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class UsesthisSpider(CrawlSpider):
    """
    Starting at http://usesthis.com/interviews, parse each interview article
    into a PersonItem (each containing a list of ToolsItems).
    If possible, navigate the "next" link and repeat the process.
    """
    rules = (
        Rule(LinkExtractor(restrict_css='article.interviewee.h-card.vcard a.p-name'), callback='parse_article'),
        Rule(LinkExtractor(restrict_css='a#next')),
    )

    def parse_article(self, response):
        # Initialize some I/O processors
        join_all = Join('')
        take_first = TakeFirst()
        identity = Identity()
        prepend_url = PrependResponseUrl(response.url)
        strip_all, strip_one = StripAll(), StripOne()
        add_space_after_punct = AddSpaceAfterPunct()

        # Load PersonItem
        person_loader = ItemLoader(item=PersonItem(), response=response)
        person_loader.default_output_processor = take_first
        person_loader.add_css('name', 'h3.p-name::text', strip_all)
        person_loader.add_value('article_url', response.url)
        person_loader.add_css('pub_date', 'time.dt-published::attr(datetime)')
        person_loader.add_css('title', 'p.summary.p-summary::text', strip_all)
        person_loader.add_css('img_src', 'img.portrait::attr(src)', prepend_url)
        person_loader.add_xpath('bio', '//div[@class="e-content"]/p[count(preceding-sibling::h4)=1]/descendant-or-self::*/text()', join_all, add_space_after_punct)
        person_loader.add_xpath('hardware', '//div[@class="e-content"]/p[count(preceding-sibling::h4)=2]/descendant-or-self::*/text()', join_all, add_space_after_punct)
        person_loader.add_xpath('software', '//div[@class="e-content"]/p[count(preceding-sibling::h4)=3]/descendant-or-self::*/text()', join_all, add_space_after_punct)
        person_loader.add_xpath('dream', '//div[@class="e-content"]/p[count(preceding-sibling::h4)=4]/descendant-or-self::*/text()', join_all, add_space_after_punct)
        person_item = person_loader.load_item()

        # @gbrener 8/16/2015: The following line causes a NotImplementedError
        #object.__setattr__(person_item, 'export_empty_fields', True)
        person_item.fill_empty_fields()

        # Load a list of ToolItems
        tool_items = []
        for tool_selector in response.css('div.e-content p a'):
            tool_loader = ItemLoader(item=ToolItem(), selector=tool_selector, response=response)
            tool_loader.default_output_processor = take_first
            tool_loader.add_xpath('tool_name', './descendant-or-self::*/text()', join_all, strip_one)
            tool_loader.add_xpath('tool_url', './@href')
            tool_item = tool_loader.load_item()

            # @gbrener 8/16/2015: The following line causes a NotImplementedError
            #object.__setattr__(tool_item, 'export_empty_fields', True)
            tool_item.fill_empty_fields()

            tool_items.append(tool_item)

        yield dict(person=person_item, tools=tool_items)


class PrependResponseUrl(object):
    def __init__(self, url):
        self.url = url
    def __call__(self, hrefs):
        return [urlparse.urljoin(self.url, href) for href in hrefs]

class StripAll(object):
    def __call__(self, text):
        return [txt.strip() for txt in text]

class StripOne(object):
    def __call__(self, text):
        return text.strip()

class AddSpaceAfterPunct(object):
    def __call__(self, text):
        return re.sub(r'([.?!])([^ .?!)])', r'\1 \2', text).strip()
