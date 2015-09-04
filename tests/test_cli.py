import unittest
import os
import shutil
from mock import patch, DEFAULT
from usesthis_crawler.cli import main
from usesthis_crawler.pipelines import ValidationPipeline


class ConfigCheckingTestCase(unittest.TestCase):
    def assertSettingEquals(self, settings, setting_name, value):
        self.assertIn(setting_name, settings.attributes)
        self.assertEquals(settings.attributes[setting_name].value, value)

    def assertSettingGreater(self, settings, setting_name, value):
        self.assertIn(setting_name, settings.attributes)
        self.assertGreater(settings.attributes[setting_name].value, value)

    def assertSettingGreaterEqual(self, settings, setting_name, value):
        self.assertIn(setting_name, settings.attributes)
        self.assertGreaterEqual(settings.attributes[setting_name].value, value)

    def assertDictSettingIsNotNone(self, settings, dict_name, setting_name):
        self.assertIn(dict_name, settings.attributes)
        self.assertIn(setting_name, settings.attributes[dict_name].value)
        self.assertIsNotNone(
            settings.attributes[dict_name].value[setting_name]
        )

    def assertDictSettingIsNone(self, settings, dict_name, setting_name):
        self.assertIn(dict_name, settings.attributes)
        self.assertIn(setting_name, settings.attributes[dict_name].value)
        self.assertIsNone(settings.attributes[dict_name].value[setting_name])


class CmdlineArgsTestCase(ConfigCheckingTestCase):
    def setUp(self):
        for path in ('some-test-dir', 'path-to-interviews.db'):
            if os.path.exists(path):
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)

    def tearDown(self):
        for path in ('some-test-dir', 'path-to-interviews.db'):
            if os.path.exists(path):
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)

    def test_default_args(self):
        """Test that the program works as expected when no arguments are provided.
        """
        with patch('usesthis_crawler.cli.CrawlerProcess', autospec=True) \
             as process_mock:
            main([''])

        self.assertTrue(process_mock.called)

        settings = process_mock.call_args[0][0]

        self.assertSettingEquals(settings, 'LOG_ENABLED', True)
        self.assertSettingEquals(settings, 'LOG_LEVEL', 'ERROR')
        self.assertDictSettingIsNotNone(settings, 'ITEM_PIPELINES', 'usesthis_crawler.pipelines.ValidationPipeline')
        self.assertDictSettingIsNotNone(settings, 'ITEM_PIPELINES', 'usesthis_crawler.pipelines.SQLPipeline')
        self.assertDictSettingIsNotNone(settings, 'EXTENSIONS', 'scrapy.extensions.closespider.CloseSpider')
        self.assertSettingGreaterEqual(settings, 'CLOSESPIDER_ERRORCOUNT', 1)

    def test_debug_mode_works(self):
        """Verify that debug-mode can be enabled via the command-line.
        """
        with patch('usesthis_crawler.cli.CrawlerProcess', autospec=True) \
             as process_mock:
            main(['', '-t'])

        self.assertTrue(process_mock.called)

        settings = process_mock.call_args[0][0]

        self.assertSettingEquals(settings, 'LOG_ENABLED', True)
        self.assertSettingEquals(settings, 'LOG_LEVEL', 'DEBUG')
        self.assertDictSettingIsNotNone(settings, 'EXTENSIONS', 'scrapy.extensions.closespider.CloseSpider')
        self.assertSettingGreater(settings, 'CLOSESPIDER_PAGECOUNT', 0)

    def test_debug_mode_overrides_log_level(self):
        """Verify that when debug-mode is enabled via the command-line, any log-level command-line setting will be overridden.
        """
        with patch('usesthis_crawler.cli.CrawlerProcess', autospec=True) \
             as process_mock:
            main(['', '-t', '-l', 'INFO'])

        self.assertTrue(process_mock.called)

        settings = process_mock.call_args[0][0]

        self.assertSettingEquals(settings, 'LOG_ENABLED', True)
        self.assertSettingEquals(settings, 'LOG_LEVEL', 'DEBUG')
        self.assertDictSettingIsNotNone(settings, 'EXTENSIONS', 'scrapy.extensions.closespider.CloseSpider')
        self.assertSettingGreater(settings, 'CLOSESPIDER_PAGECOUNT', 0)

    def test_skip_db_mode_works(self):
        """Verify that the skip-database feature can be enabled via the command-line.
        """
        with patch('usesthis_crawler.cli.CrawlerProcess', autospec=True) \
             as process_mock:
            main(['', '-s'])

        self.assertTrue(process_mock.called)

        settings = process_mock.call_args[0][0]

        self.assertDictSettingIsNone(settings, 'ITEM_PIPELINES', 'usesthis_crawler.pipelines.SQLPipeline')

    def test_no_validation_mode_works(self):
        """Verify that the no-validation feature can be enabled via the command-line.
        """
        with patch('usesthis_crawler.cli.CrawlerProcess', autospec=True) \
             as process_mock:
            main(['', '-n'])

        self.assertTrue(process_mock.called)

        settings = process_mock.call_args[0][0]

        self.assertDictSettingIsNone(settings, 'ITEM_PIPELINES', 'usesthis_crawler.pipelines.ValidationPipeline')

    def test_log_level_info_works(self):
        """Verify that the log-level option can be set to 'INFO' via the command-line.
        """
        with patch('usesthis_crawler.cli.CrawlerProcess', autospec=True) \
             as process_mock:
            main(['', '-l', 'INFO'])

        self.assertTrue(process_mock.called)

        settings = process_mock.call_args[0][0]

        self.assertSettingEquals(settings, 'LOG_ENABLED', True)
        self.assertSettingEquals(settings, 'LOG_LEVEL', 'INFO')

    def test_log_level_error_works(self):
        """Verify that the log-level option can be set to 'ERROR' via the command-line.
        """
        with patch('usesthis_crawler.cli.CrawlerProcess', autospec=True) \
             as process_mock:
            main(['', '-l', 'ERROR'])

        self.assertTrue(process_mock.called)

        settings = process_mock.call_args[0][0]

        self.assertSettingEquals(settings, 'LOG_ENABLED', True)
        self.assertSettingEquals(settings, 'LOG_LEVEL', 'ERROR')

    def test_log_level_warn_works(self):
        """Verify that the log-level option can be set to 'WARN' via the command-line.
        """
        with patch('usesthis_crawler.cli.CrawlerProcess', autospec=True) \
             as process_mock:
            main(['', '-l', 'WARN'])

        self.assertTrue(process_mock.called)

        settings = process_mock.call_args[0][0]

        self.assertSettingEquals(settings, 'LOG_ENABLED', True)
        self.assertSettingEquals(settings, 'LOG_LEVEL', 'WARN')

    def test_log_level_debug_works(self):
        """Verify that the log-level option can be set to 'DEBUG' via the command-line.
        """
        with patch('usesthis_crawler.cli.CrawlerProcess', autospec=True) \
             as process_mock:
            main(['', '-l', 'DEBUG'])

        self.assertTrue(process_mock.called)

        settings = process_mock.call_args[0][0]

        self.assertSettingEquals(settings, 'LOG_ENABLED', True)
        self.assertSettingEquals(settings, 'LOG_LEVEL', 'DEBUG')

    def test_db_path_works(self):
        """Verify that the database path can be changed via the command-line.
        """
        with patch('usesthis_crawler.cli.CrawlerProcess', autospec=True) \
             as process_mock:
            main(['', '-d', 'path-to-interviews.db'])

        self.assertTrue(process_mock.called)

        settings = process_mock.call_args[0][0]

        self.assertSettingEquals(settings, 'DB_PATH', 'path-to-interviews.db')

    def test_db_path_creates_dirs(self):
        """Verify that the database directories will be created (if necessary) after the database-path is changed via the command-line.
        """
        self.assertFalse(os.path.exists('some-test-dir/here'))

        with patch('usesthis_crawler.cli.CrawlerProcess', autospec=True) \
             as process_mock:
            main(['', '-d', 'some-test-dir/here/path-to-db'])

        self.assertTrue(process_mock.called)

        settings = process_mock.call_args[0][0]

        self.assertSettingEquals(settings, 'DB_PATH', 'some-test-dir/here/path-to-db')
        self.assertTrue(os.path.exists('some-test-dir/here'))

    def test_db_path_is_ok_with_dirs(self):
        """Verify that there won't be any problems if the database directory already exists, and but the database-path is changed via the command-line.
        """
        os.makedirs('some-test-dir/here')
        self.assertTrue(os.path.exists('some-test-dir/here'))

        with patch('usesthis_crawler.cli.CrawlerProcess', autospec=True) \
             as process_mock:
            main(['', '-d', 'some-test-dir/here/path-to-db'])

        self.assertTrue(process_mock.called)

        settings = process_mock.call_args[0][0]

        self.assertSettingEquals(settings, 'DB_PATH', 'some-test-dir/here/path-to-db')
        self.assertTrue(os.path.exists('some-test-dir/here'))

    def test_db_replace_works_no_db(self):
        """Verify that the "replace database" option can be set via the command-line when there is no existing database.
        """
        os.makedirs('some-test-dir/here')
        self.assertTrue(os.path.exists('some-test-dir/here'))
        self.assertFalse(os.path.exists('some-test-dir/here/test.db'))

        with patch('usesthis_crawler.cli.CrawlerProcess', autospec=True) \
             as process_mock:
            main(['', '-d', 'some-test-dir/here/test.db', '-r'])

        self.assertTrue(process_mock.called)

        settings = process_mock.call_args[0][0]

        self.assertSettingEquals(settings, 'DB_PATH', 'some-test-dir/here/test.db_new')
        self.assertTrue(os.path.exists('some-test-dir/here/test.db'))
        self.assertFalse(os.path.exists('some-test-dir/here/test.db_new'))

    def test_db_replace_works(self):
        """Verify that the "replace database" option can be set via the command-line when there is an existing database. Not a great test - as file-creation time isn't checked (it's not available on all OSes).
        """
        os.makedirs('some-test-dir/here')
        self.assertTrue(os.path.exists('some-test-dir/here'))
        open('some-test-dir/here/test.db', 'w').close()
        self.assertTrue(os.path.exists('some-test-dir/here/test.db'))

        with patch('usesthis_crawler.cli.CrawlerProcess', autospec=True) \
             as process_mock:
            main(['', '-d', 'some-test-dir/here/test.db', '-r'])

        self.assertTrue(process_mock.called)

        settings = process_mock.call_args[0][0]

        self.assertSettingEquals(settings, 'DB_PATH', 'some-test-dir/here/test.db_new')
        self.assertTrue(os.path.exists('some-test-dir/here/test.db'))
        self.assertFalse(os.path.exists('some-test-dir/here/test.db_new'))

    def test_verbose_works(self):
        """Verify that the verbose option can be enabled via the command-line.
        """
        with patch('usesthis_crawler.cli.CrawlerProcess', autospec=True) \
             as process_mock:
            main(['', '-v'])

        self.assertTrue(process_mock.called)

        settings = process_mock.call_args[0][0]

        self.assertSettingEquals(settings, 'LOG_ENABLED', True)
        self.assertSettingEquals(settings, 'LOG_LEVEL', 'DEBUG')
        self.assertTrue(ValidationPipeline._verbose)

    def test_verbose_overrides_log_level(self):
        """Verify that when the verbose option is enabled via the command-line, it will override the log-level's setting.
        """
        with patch('usesthis_crawler.cli.CrawlerProcess', autospec=True) \
             as process_mock:
            main(['', '-l', 'INFO', '-v'])

        self.assertTrue(process_mock.called)

        settings = process_mock.call_args[0][0]

        self.assertSettingEquals(settings, 'LOG_ENABLED', True)
        self.assertSettingEquals(settings, 'LOG_LEVEL', 'DEBUG')
        self.assertTrue(ValidationPipeline._verbose)

