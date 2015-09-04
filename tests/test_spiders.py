import unittest
import scrapy
import requests
import urlparse
import re
from mock import patch
from usesthis_crawler.spiders.usesthis import UsesthisSpider
from usesthis_crawler.items import PersonItem, ToolItem


class UsesthisHTTPTestCase(unittest.TestCase):
    def setUp(self):
        self.spider = UsesthisSpider('usesthis')
        self.session = requests.Session()

    def tearDown(self):
        self.session.close()

    def assertIsArticleRequest(self, request):
        url_comps = urlparse.urlparse(request.url)
        self.assertEquals(request.headers, {})
        self.assertEquals(request.method, 'GET')
        self.assertEquals(request.callback, self.spider.parse_article)
        self.assertEquals(url_comps.scheme, 'https')
        self.assertEquals(url_comps.netloc, 'usesthis.com')
        self.assertTrue(url_comps.path.startswith('/interviews/'))

    def assertIsNextPageRequest(self, request):
        url_comps = urlparse.urlparse(request.url)
        self.assertEquals(request.headers, {})
        self.assertEquals(request.method, 'GET')
        self.assertEquals(request.callback, None)
        self.assertEquals(url_comps.scheme, 'https')
        self.assertEquals(url_comps.netloc, 'usesthis.com')
        self.assertTrue(url_comps.path.startswith('/interviews/page'))

    def assertItemFilled(self, item):
        self.assertFalse(set(item.fields) - set(item))


class UsesthisSpiderTestCase(UsesthisHTTPTestCase):
    def test_parses_article_links(self):
        """Verify that UsesthisSpider.parse() finds all article links and 'next' link at the starting "interviews" URL.
        """
        response_obj = self.session.get('https://usesthis.com/interviews/')
        response = scrapy.http.HtmlResponse(
            url='https://usesthis.com/interviews/',
            body=response_obj.text,
            encoding='utf-8',
        )
        spider_requests = list(iter(self.spider.parse(response)))
        p2_request = spider_requests.pop()

        self.assertIsNextPageRequest(p2_request)

        self.assertGreater(spider_requests, 1)
        for request in spider_requests:
            self.assertIsArticleRequest(request)

            article_response_obj = self.session.get(request.url)
            article_response = scrapy.http.HtmlResponse(
                url=request.url,
                body=article_response_obj.text,
                encoding='utf-8',
            )
            for item in request.callback(article_response):
                person_item = item['person']
                self.assertTrue(isinstance(person_item, PersonItem))
                self.assertItemFilled(person_item)

                for tool_item in item['tools']:
                    self.assertTrue(isinstance(tool_item, ToolItem))
                    self.assertItemFilled(tool_item)

    def test_parses_no_links(self):
        """Verify that UsesthisSpider.parse() works properly when there are no links on the page.
        """
        response_obj = self.session.get('https://usesthis.com/interviews/')
        # Quick and dirty
        response_body = re.sub(r'<a .+</a>', '', response_obj.text)
        self.assertFalse('<a ' in response_body)

        response = scrapy.http.HtmlResponse(
            url='https://usesthis.com/interviews/',
            body=response_body,
            encoding='utf-8',
        )
        spider_requests = list(iter(self.spider.parse(response)))
        self.assertFalse(spider_requests)

    def test_parses_article_no_text(self):
        """Verify that UsesthisSpider.parse_article() constructs a PersonItem even when there is no text on the page.
        """
        response = scrapy.http.HtmlResponse(
            url='https://usesthis.com/interviews/mel.croucher',
            body='',
        )
        spider_items = list(iter(self.spider.parse_article(response)))

        self.assertEquals(len(spider_items), 1)
        self.assertEquals(
            spider_items[0]['person'],
            PersonItem(
                name='',
                title='',
                article_url='https://usesthis.com/interviews/mel.croucher',
                bio='',
                hardware='',
                software='',
                dream='',
                img_src='',
                pub_date='',
            )
        )
        self.assertEquals(spider_items[0]['tools'], [])
