# -*- coding: utf-8 -*-

import sys
from sqlalchemy.exc import IntegrityError
from scrapy.exceptions import DropItem
from usesthis_crawler import Session, logger
from usesthis_crawler.models import Person, Tool
from usesthis_crawler.validation import \
    ItemValidationError, validate_person_item, validate_tool_items
from sqlalchemy import create_engine


class ValidationPipeline(object):
    def process_item(self, item, spider):
        """Raise DropItem exception if the PersonItem component is not valid.
        Otherwise, delete any ToolItem components that are not valid.
        Return the input item, less any invalid ToolItem components.

        Arguments:
            - item: dictionary {'person': PersonItem component,
                                'tools': list of ToolItem components}
            - spider: a spider instance (see scrapy docs)

        Returns:
            - item: dictionary {'person': PersonItem component,
                                'tools': list of ToolItem components}
        """
        try:
            validate_person_item(item['person'], verbose=self._verbose)
        except ItemValidationError, exc:
            raise DropItem(exc.message)
        validate_tool_items(item['tools'], item['person'], verbose=self._verbose)
        return item


class SQLPipeline(object):
    def open_spider(self, spider):
        """Create a SQLAlchemy session.
        Note: this gets called implicitly by scrapy.
        """
        self.session = Session()

    def close_spider(self, spider):
        """Close the SQLAlchemy session.
        Note: this gets called implicitly by scrapy.
        """
        self.session.close()

    def process_item(self, item, spider):
        """Add the PersonItem component and the list of ToolItem components to
        the database. Return the input item.
        If a database constraint is violated, rollback the transaction.

        Arguments:
            - item: dictionary {'person': PersonItem component,
                                'tools': list of ToolItem components}
            - spider: a spider instance (see scrapy docs)

        Returns:
            - item: dictionary {'person': PersonItem component,
                                'tools': list of ToolItem components}

        Note: the "rollback" behavior is currently untestable by SQLAlchemy.
        """
        person = Person(**item['person'])

        for tool_item in item['tools']:
            tool = Tool(**tool_item)
            person.tools.append(tool)

        self.session.add(person)
        try:
            self.session.commit()
            sys.stderr.write('.')
        except IntegrityError:
            logger.warn('"%s" is already in database.', person.name)
            self.session.rollback()

        return item
