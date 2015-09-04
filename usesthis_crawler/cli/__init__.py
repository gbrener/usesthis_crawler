#!/usr/bin/env python

import os
import sys
import argparse
import shutil
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings, ENVVAR
from usesthis_crawler import logger
from usesthis_crawler.spiders.usesthis import UsesthisSpider
from usesthis_crawler.models import init_models
from usesthis_crawler.pipelines import ValidationPipeline


SCRIPTDIR = os.path.dirname(os.path.realpath(__file__))


class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                    argparse.RawTextHelpFormatter):
    pass


class ArgParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(ArgParser, self).__init__(*args, **kwargs)

        self.add_argument(
            '-t', '--test',
            help='enable debug-mode',
            action='store_true',
        )

        self.add_argument(
            '-s', '--skip-database',
            help='disable writing to the database',
            action='store_true',
        )

        self.add_argument(
            '-n', '--no-validate',
            help='avoid validating items after they\'re scraped',
            action='store_true',
        )

        log_levels = list(reversed(['DEBUG', 'WARN', 'ERROR', 'INFO']))
        self.add_argument(
            '-l', '--log-level',
            help='set the logging level',
            choices=log_levels,
            default='ERROR',
        )

        self.add_argument(
            '-d', '--db-path',
            help='path to where the database should be created/updated',
            default=os.path.join(SCRIPTDIR, '..', 'db', 'interviews.db'),
        )

        self.add_argument(
            '-r', '--replace-database',
            help='replace the database entirely, instead of updating it',
            action='store_true',
        )

        self.add_argument(
            '-v', '--verbose',
            help='show more helpful error messages',
            action='store_true',
        )


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = ArgParser(prog=argv[0],
                       formatter_class=HelpFormatter,
                       description='Scrape usesthis.com for people and tools.')
    args = parser.parse_args(args=argv[1:])

    settings = get_project_settings()

    settings.attributes['DB_PATH'].value = args.db_path
    db_dir = os.path.dirname(args.db_path)
    if not os.path.exists(db_dir) and db_dir:
        os.makedirs(db_dir)
        logger.info('Created database directory: %s', db_dir)

    if args.replace_database:
        settings.attributes['DB_PATH'].value = args.db_path+'_new'
        old_db_exists = os.path.exists(args.db_path)
        if not old_db_exists:
            logger.info('No previous database exists, so a new one will be created ("replace-database" option has no effect).')
        else:
            logger.info('Database will be replaced.')

    if (settings.attributes['LOG_LEVEL'].value != args.log_level and
        not args.verbose):
        settings.attributes['LOG_LEVEL'].value = args.log_level
        logger.info('Log level set to %s.', args.log_level)

    if args.test:
        settings.attributes['LOG_LEVEL'].value = 'DEBUG'
        settings.attributes['CLOSESPIDER_PAGECOUNT'].value = 2
        logger.info('Debug-mode enabled.')

    if args.no_validate:
        settings.attributes['ITEM_PIPELINES'].value['usesthis_crawler.pipelines.ValidationPipeline'] = None
        logger.info('ValidationPipeline disabled.')

    if args.skip_database:
        settings.attributes['ITEM_PIPELINES'].value['usesthis_crawler.pipelines.SQLPipeline'] = None
        logger.info('SQLPipeline disabled.')
    else:
        init_models(settings.attributes['DB_PATH'].value, args.test)

    ValidationPipeline._verbose = False
    if args.verbose:
        ValidationPipeline._verbose = True
        settings.attributes['LOG_LEVEL'].value = 'DEBUG'

    process = CrawlerProcess(settings)

    process.crawl(
        UsesthisSpider,
        name='usesthis',
        allowed_domains=['usesthis.com'],
        start_urls=(
            'https://usesthis.com/interviews/',
        ),
    )

    process.start()

    if args.replace_database:
        if old_db_exists:
            os.remove(args.db_path)
        os.rename(args.db_path+'_new', args.db_path)

    return 0
