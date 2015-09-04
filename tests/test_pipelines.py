import logging
import unittest
import hypothesis.strategies as st
from hypothesis import given
from scrapy.exceptions import DropItem
from sqlalchemy import create_engine
from usesthis_crawler import logger, Session
from usesthis_crawler.pipelines import ValidationPipeline, SQLPipeline
from usesthis_crawler.items import PersonItem, ToolItem
from usesthis_crawler.spiders.usesthis import UsesthisSpider
from usesthis_crawler.models import Base, Person, Tool, people_to_tools_tbl

class ValidationPipelineTestCase(unittest.TestCase):
    def setUp(self):
        logger.setLevel(logging.CRITICAL)

    @given(
        item=st.fixed_dictionaries(
            dict(
                person=st.builds(
                    PersonItem,
                    st.fixed_dictionaries(
                        dict(
                            name=st.text(min_size=1),
                            article_url=st.just('https://usesthis.com/interviews/joe.schmoe/'),
                            pub_date=st.just('2014-04-08'),
                            title=st.text(),
                            img_src=st.just('https://usesthis.com/images/portraits/joe.schmoe.jpg'),
                            bio=st.text(),
                            hardware=st.text(),
                            software=st.text(),
                            dream=st.text(),
                        )
                    )
                ),
                tools=st.lists(
                    st.builds(
                        ToolItem,
                        st.fixed_dictionaries(
                            dict(
                                tool_name=st.text(min_size=1),
                                tool_url=st.just('http://plumbertools.org/pipebuster5000'),
                            )
                        )
                    )
                )
            )
        ),
        verbose=st.booleans(),
    )
    def test_item_validated_and_returned(self, item, verbose):
        """Verify that when the ValidationPipeline receives a correctly-constructed item, it returns the very same item after validating it.
        """
        spider = UsesthisSpider('usesthis')
        pipeline = ValidationPipeline()
        pipeline._verbose = verbose
        same_item = pipeline.process_item(item, spider)
        self.assertEquals(same_item, item)

    @given(
        item=st.fixed_dictionaries(
            dict(
                person=st.builds(
                    PersonItem,
                    st.lists(
                        st.sampled_from([
                            ('name', 'Joe Schmoe'),
                            ('article_url', 'https://usesthis.com/interviews/joe.schmoe/'),
                            ('pub_date', '2014-04-08'),
                            ('title', 'Plumber'),
                            ('img_src', 'https://usesthis.com/images/portraits/joe.schmoe.jpg'),
                            ('bio', 'Hi, my name is Joe. People call me "Joe the Plumber".'),
                            ('hardware', 'I use the PipeBuster5000. Best wrench on the market.'),
                            ('software', 'I couldn\'t care less about software.'),
                            ('dream', 'My dream setup would be a PipeBuster6000.'),
                        ]),
                        min_size=0,
                        max_size=len(PersonItem.fields)-1,
                        unique_by=lambda x: x
                    ),
                ),
                tools=st.lists(
                    st.builds(
                        ToolItem,
                        st.fixed_dictionaries(
                            dict(
                                tool_name=st.text(min_size=1),
                                tool_url=st.just('http://plumbertools.org/pipebuster5000'),
                            )
                        )
                    )
                )
            )
        ),
        verbose=st.booleans(),
    )
    def test_drop_person_missing_field(self, item, verbose):
        """Verify that the ValidationPipeline drops the PersonItem instance if it's missing one or more fields.
        """
        spider = UsesthisSpider('usesthis')
        pipeline = ValidationPipeline()
        pipeline._verbose = verbose
        with self.assertRaises(DropItem):
            returned_item = pipeline.process_item(item, spider)
            self.assertIsNone(returned_item)

    @given(
        item=st.fixed_dictionaries(
            dict(
                person=st.builds(
                    PersonItem,
                    st.fixed_dictionaries(
                        dict(
                            name=st.text(min_size=1),
                            article_url=st.just('https://usesthis.com/interviews/joe.schmoe/'),
                            pub_date=st.just('2014-04-08'),
                            title=st.text(),
                            img_src=st.just('https://usesthis.com/images/portraits/joe.schmoe.jpg'),
                            bio=st.text(),
                            hardware=st.text(),
                            software=st.text(),
                            dream=st.text(),
                        )
                    )
                ),
                tools=st.lists(
                    st.builds(
                        ToolItem,
                        st.lists(
                            st.sampled_from([
                                ('tool_name', 'PipeBuster5000'),
                                ('tool_url', 'http://plumbertools.org/pipebuster5000'),
                            ]),
                            min_size=0,
                            max_size=len(ToolItem.fields),
                            unique_by=lambda x: x),
                    ),
                    min_size=1,
                    max_size=4,
                    unique_by=lambda x: tuple(x)
                )
            )
        ),
        verbose=st.booleans(),
    )
    def test_drop_tools_missing_field(self, item, verbose):
        """Verify that the ValidationPipeline deletes tool_items if they're missing one or more fields.
        """
        spider = UsesthisSpider('usesthis')
        pipeline = ValidationPipeline()
        pipeline._verbose = verbose
        clean_item = pipeline.process_item(item, spider)
        for tool_item in clean_item['tools']:
            missing_fields = set(ToolItem.fields) - set(tool_item)
            self.assertFalse(missing_fields)

    @given(
        item=st.fixed_dictionaries(
            dict(
                person=st.builds(
                    PersonItem,
                    st.fixed_dictionaries(
                        dict(
                            name=st.sampled_from(('Joe Schmoe', '')),
                            article_url=st.sampled_from(('https://usesthis.com/interviews/joe.schmoe/', '')),
                            pub_date=st.sampled_from(('2014-04-08', '')),
                            title=st.just('Plumber'),
                            img_src=st.sampled_from(('https://usesthis.com/images/portraits/joe.schmoe.jpg', '')),
                            bio=st.just('Hi, my name is Joe. People call me "Joe the Plumber".'),
                            hardware=st.just('I use the PipeBuster5000. Best wrench on the market.'),
                            software=st.just('I couldn\'t care less about software.'),
                            dream=st.just('My dream setup would be a PipeBuster6000.'),
                        )
                    )
                ),
                tools=st.lists(
                    st.builds(
                        ToolItem,
                        st.fixed_dictionaries(
                            dict(
                                tool_name=st.text(min_size=1),
                                tool_url=st.just('http://plumbertools.org/pipebuster5000'),
                            )
                        )
                    )
                )
            )
        ),
        verbose=st.booleans(),
    )
    def test_drop_person_blank_reqd_field(self, item, verbose):
        """Verify that the ValidationPipeline drops the PersonItem instance if one or more of the following fields are empty:
        name, article_url, pub_date, img_src
        """
        spider = UsesthisSpider('usesthis')
        pipeline = ValidationPipeline()
        pipeline._verbose = verbose
        if '' in item['person'].values():
            with self.assertRaises(DropItem):
                returned_item = pipeline.process_item(item, spider)
                self.assertIsNone(returned_item)
        else:
            self.assertEquals(pipeline.process_item(item, spider), item)

    @given(
        item=st.fixed_dictionaries(
            dict(
                person=st.builds(
                    PersonItem,
                    st.fixed_dictionaries(
                        dict(
                            name=st.just('Joe Schmoe'),
                            article_url=st.sampled_from((
                                'https://usesthis.com/interviews/joe.schmoe/',
                                'htt://usesthis.com/interviews/joe.schmoe/',
                                'http',
                                'http://',
                                'hhttp://usesthis.com/interviews/joe.schmoe/',
                                'http:/usesthis.com/interviews/joe.schmoe/'
                            )),
                            pub_date=st.sampled_from((
                                '2014-04-08',
                                '2014-04-33',
                                '2014-13-03',
                                '20140-12-03',
                                '2014-120-03',
                                '2014-12-030',
                                '201-12-03',
                                '2014-1-03',
                                '2014-01-3',
                                '2014-01-3',
                                '20140103',
                                '01032014',
                                '14-04-08',
                                '04-08-14'
                            )),
                            title=st.just('Plumber'),
                            img_src=st.sampled_from((
                                'https://usesthis.com/images/portraits/joe.schmoe.jpg',
                                'ttps://usesthis.com/images/portraits/joe.schmoe.jpg',
                                'http',
                                'http://',
                                'https://usesthis.com/images/portraits/joe.schmoe.',
                                'hhttps://usesthis.com/images/portraits/joe.schmoe.jpg',
                                'https://usesthis.com/images/portraits/joe.schmoe.png', # needs 'jpg' extension
                            )),
                            bio=st.just('Hi, my name is Joe. People call me "Joe the Plumber".'),
                            hardware=st.just('I use the PipeBuster5000. Best wrench on the market.'),
                            software=st.just('I couldn\'t care less about software.'),
                            dream=st.just('My dream setup would be a PipeBuster6000.'),
                        )
                    )
                ),
                tools=st.lists(
                    st.builds(
                        ToolItem,
                        st.fixed_dictionaries(
                            dict(
                                tool_name=st.text(min_size=1),
                                tool_url=st.just('http://plumbertools.org/pipebuster5000'),
                            )
                        )
                    )
                )
            )
        ),
        verbose=st.booleans(),
    )
    def test_drop_person_malformed_url_or_date(self, item, verbose):
        """Verify that the ValidationPipeline drops the PersonItem instance if it has a malformed url or date.
        """
        spider = UsesthisSpider('usesthis')
        pipeline = ValidationPipeline()
        pipeline._verbose = verbose
        try:
            with self.assertRaises(DropItem):
                returned_item = pipeline.process_item(item, spider)
                self.assertIsNone(returned_item)
        except AssertionError:
            self.assertEquals(returned_item['person'], PersonItem(
                name='Joe Schmoe',
                article_url='https://usesthis.com/interviews/joe.schmoe/',
                pub_date='2014-04-08',
                title='Plumber',
                img_src='https://usesthis.com/images/portraits/joe.schmoe.jpg',
                bio='Hi, my name is Joe. People call me "Joe the Plumber".',
                hardware='I use the PipeBuster5000. Best wrench on the market.',
                software='I couldn\'t care less about software.',
                dream='My dream setup would be a PipeBuster6000.',
            ))

    @given(
        item=st.fixed_dictionaries(
            dict(
                person=st.builds(
                    PersonItem,
                    st.fixed_dictionaries(
                        dict(
                            name=st.text(min_size=1),
                            article_url=st.just('https://usesthis.com/interviews/joe.schmoe/'),
                            pub_date=st.just('2014-04-08'),
                            title=st.text(),
                            img_src=st.just('https://usesthis.com/images/portraits/joe.schmoe.jpg'),
                            bio=st.text(),
                            hardware=st.text(),
                            software=st.text(),
                            dream=st.text(),
                        )
                    )
                ),
                tools=st.lists(
                    st.builds(
                        ToolItem,
                        st.fixed_dictionaries(
                            dict(
                                tool_name=st.sampled_from(('PipeBuster5000', '')),
                                tool_url=st.sampled_from(('http://plumbertools.org/pipebuster5000', '')),
                            )
                        )
                    )
                )
            )
        ),
        verbose=st.booleans(),
    )
    def test_drop_tool_blank_reqd_field(self, item, verbose):
        """Verify that the ValidationPipeline drops a ToolItem instance if it has no tool_name or no tool_url.
        """
        spider = UsesthisSpider('usesthis')
        pipeline = ValidationPipeline()
        pipeline._verbose = verbose
        clean_item = pipeline.process_item(item, spider)
        for tool_item in clean_item['tools']:
            for val in tool_item.values():
                self.assertTrue(val)

    @given(
        item=st.fixed_dictionaries(
            dict(
                person=st.builds(
                    PersonItem,
                    st.fixed_dictionaries(
                        dict(
                            name=st.text(min_size=1),
                            article_url=st.just('https://usesthis.com/interviews/joe.schmoe/'),
                            pub_date=st.just('2014-04-08'),
                            title=st.text(),
                            img_src=st.just('https://usesthis.com/images/portraits/joe.schmoe.jpg'),
                            bio=st.text(),
                            hardware=st.text(),
                            software=st.text(),
                            dream=st.text(),
                        )
                    )
                ),
                tools=st.lists(
                    st.builds(
                        ToolItem,
                        st.fixed_dictionaries(
                            dict(
                                tool_name=st.just('PipeBuster5000'),
                                tool_url=st.sampled_from((
                                    'http://plumbertools.org/pipebuster5000',
                                    'hhttp://plumbertools.org/pipebuster5000',
                                    'htt://plumbertools.org/pipebuster5000',
                                    'http:://plumbertools.org/pipebuster5000',
                                    'http:/plumbertools.org/pipebuster5000',
                                    ':/plumbertools.org/pipebuster5000)',
                                ))
                            )
                        )
                    )
                )
            )
        ),
        verbose=st.booleans(),
    )
    def test_drop_tool_malformed_url(self, item, verbose):
        """Verify that the ValidationPipeline drops a ToolItem instance if it has a malformed tool_url.
        """
        spider = UsesthisSpider('usesthis')
        pipeline = ValidationPipeline()
        pipeline._verbose = verbose
        clean_item = pipeline.process_item(item, spider)
        # The only remaining tools should be from the one 'correct' URL
        for tool_item in clean_item['tools']:
            tool_url = tool_item['tool_url']
            self.assertEquals(tool_url, 'http://plumbertools.org/pipebuster5000')


class SQLPipelineTestCase(unittest.TestCase):
    def setup_example(self):
        engine = create_engine('sqlite:///:memory:') #, echo=True)
        self.connection = engine.connect()
        self.transaction = self.connection.begin()
        self.session = Session(bind=self.connection)
        Base.metadata.create_all(engine)

    def teardown_example(self, _):
        self.session.close()
        self.transaction.rollback()
        self.connection.close()

    @given(
        st.fixed_dictionaries(
            dict(
                person=st.builds(
                    PersonItem,
                    st.fixed_dictionaries(
                        dict(
                            name=st.text(min_size=1),
                            article_url=st.just('https://usesthis.com/interviews/joe.schmoe/'),
                            pub_date=st.just('2014-04-08'),
                            title=st.text(),
                            img_src=st.just('https://usesthis.com/images/portraits/joe.schmoe.jpg'),
                            bio=st.text(),
                            hardware=st.text(),
                            software=st.text(),
                            dream=st.text(),
                        )
                    )
                ),
                tools=st.lists(
                    st.builds(
                        ToolItem,
                        st.fixed_dictionaries(
                            dict(
                                tool_name=st.text(min_size=1),
                                tool_url=st.just('http://plumbertools.org/pipebuster5000'),
                            )
                        )
                    )
                )
            )
        )
    )
    def test_item_added_to_database(self, item):
        """Verify that when the SQLPipeline receives a validated item - and the database doesn't already contain the item - it gets added to the database.
        """
        spider = UsesthisSpider('usesthis')
        pipeline = SQLPipeline()
        pipeline.session = self.session

        # Assert that nothing is in the relevant database tables beforehand
        self.assertFalse(self.session.query(Person).all())
        self.assertFalse(self.session.query(Tool).all())
        self.assertFalse(self.session.query(people_to_tools_tbl).all())

        # The `process_item()` method should return the same item
        same_item = pipeline.process_item(item, spider)
        self.assertEquals(same_item, item)

        # Create some Person and Tool model objects for comparison
        person = Person(**item['person'])
        person.id = 1
        tools = []
        for tool_id, tool_item in enumerate(item['tools'], start=1):
            tool = Tool(**tool_item)
            tool.id = tool_id
            tools.append(tool)

        # Assert that the correct Person model was inserted
        same_person = self.session.query(Person).one()
        self.assertEquals(same_person.id, person.id)
        self.assertEquals(same_person.name, person.name)
        self.assertEquals(same_person.pub_date, person.pub_date)
        self.assertEquals(same_person.title, person.title)
        self.assertEquals(same_person.img_src, person.img_src)
        self.assertEquals(same_person.article_url, person.article_url)
        self.assertEquals(same_person.bio, person.bio)
        self.assertEquals(same_person.hardware, person.hardware)
        self.assertEquals(same_person.software, person.software)
        self.assertEquals(same_person.dream, person.dream)

        # Assert that the correct Tool models were inserted
        same_tools = self.session.query(Tool).all()
        for tool_idx, same_tool in enumerate(same_tools):
            tool = tools[tool_idx]
            self.assertEquals(same_tool.id, tool.id)
            self.assertEquals(same_tool.tool_name, tool.tool_name)
            self.assertEquals(same_tool.tool_url, tool.tool_url)

        # Assert that the correct Person-Tool relations were inserted
        relations = self.session.query(people_to_tools_tbl).all()
        for idx, relation in enumerate(sorted(relations)):
            tool = tools[idx]
            self.assertEquals(relation.person_id, person.id)
            self.assertEquals(relation.tool_id, tool.id)

    @unittest.skip("SQLAlchemy SAVEPOINTs don't work with SQLite, so the rollback invalidates the transaction.")
    @given(
        st.fixed_dictionaries(
            dict(
                person=st.builds(
                    PersonItem,
                    st.fixed_dictionaries(
                        dict(
                            name=st.text(min_size=1),
                            article_url=st.just('https://usesthis.com/interviews/joe.schmoe/'),
                            pub_date=st.just('2014-04-08'),
                            title=st.text(),
                            img_src=st.just('https://usesthis.com/images/portraits/joe.schmoe.jpg'),
                            bio=st.text(),
                            hardware=st.text(),
                            software=st.text(),
                            dream=st.text(),
                        )
                    )
                ),
                tools=st.lists(
                    st.builds(
                        ToolItem,
                        st.fixed_dictionaries(
                            dict(
                                tool_name=st.text(min_size=1),
                                tool_url=st.just('http://plumbertools.org/pipebuster5000'),
                            )
                        )
                    )
                )
            )
        )
    )
    def test_dont_add_dup_person_to_database(self, item):
        """Verify that when the SQLPipeline receives a validated item - and the database already contains the item - it doesn't get added to the database.
        """
        spider = UsesthisSpider('usesthis')
        pipeline = SQLPipeline()
        pipeline.session = self.session

        # Create some Person and Tool model objects for comparison
        person = Person(**item['person'])
        person.id = 1
        tools = []
        for tool_id, tool_item in enumerate(item['tools'], start=1):
            tool = Tool(**tool_item)
            tool.id = tool_id
            tools.append(tool)
        self.session.add(person)

        # Assert that nothing is in the relevant database tables beforehand
        self.assertEquals(self.session.query(Person).all(), [person])
        self.assertFalse(self.session.query(Tool).all())
        self.assertFalse(self.session.query(people_to_tools_tbl).all())

        # The `process_item()` method should return the same item
        same_item = pipeline.process_item(item, spider)
        self.assertEquals(same_item, item)

        # Assert that the correct Person model was inserted
        same_person = self.session.query(Person).one()
        self.assertEquals(same_person.id, person.id)
        self.assertEquals(same_person.name, person.name)
        self.assertEquals(same_person.pub_date, person.pub_date)
        self.assertEquals(same_person.title, person.title)
        self.assertEquals(same_person.img_src, person.img_src)
        self.assertEquals(same_person.article_url, person.article_url)
        self.assertEquals(same_person.bio, person.bio)
        self.assertEquals(same_person.hardware, person.hardware)
        self.assertEquals(same_person.software, person.software)
        self.assertEquals(same_person.dream, person.dream)

        # Assert that the correct Tool models were inserted
        tools_in_db = self.session.query(Tool).all()
        self.assertFalse(tools_in_db)

        # Assert that the correct Person-Tool relations were inserted
        relations_in_db = self.session.query(people_to_tools_tbl).all()
        self.assertFalse(relations_in_db)
