# -*- coding: utf-8 -*-

# Scrapy settings for interviews project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'usesthis_crawler'

SPIDER_MODULES = ['usesthis_crawler.spiders']
NEWSPIDER_MODULE = 'usesthis_crawler.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'interviews (+http://www.yourdomain.com)'

DB_PATH = 'interviews.db'

LOG_ENABLED = True
LOG_LEVEL = 'ERROR'
ITEM_PIPELINES = {
    'usesthis_crawler.pipelines.ValidationPipeline': 400,
    'usesthis_crawler.pipelines.SQLPipeline': 500,
}

EXTENSIONS = {
    'scrapy.extensions.closespider.CloseSpider': 500,
}

CLOSESPIDER_PAGECOUNT = 0
CLOSESPIDER_ERRORCOUNT = 1
