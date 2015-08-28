"""Tests for DefaultSettings."""
import mock
import unittest

from janrain_datalib.app import App
from janrain_datalib.defaultsettings import DefaultSettings
from .mockapi import Mockapi

class TestDefaultSettings(unittest.TestCase):

    def setUp(self):
        # use a mock for the api calls
        self.mockapi = Mockapi('')

        # create the app object
        self.app = App(self.mockapi)

        # create the default settings object
        self.settings = DefaultSettings(self.app)

    def test_get_existant(self):
        # get existing setting
        key = self.mockapi.settings['default_settings'].keys()[0]
        value = self.settings.get(key)
        expected = self.mockapi.settings['default_settings'][key]
        self.assertEqual(value, expected)

        calls = [
            mock.call('settings/get_all'),
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_get_nonexistant(self):
        # get setting that does not exist
        key = 'bogus'
        value = self.settings.get(key)
        self.assertIs(value, None)

        calls = [
            mock.call('settings/get_all'),
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_get_all(self):
        all_settings = self.settings.get_all()
        self.assertEqual(all_settings, self.mockapi.settings['default_settings'])

        calls = [
            mock.call('settings/get_all'),
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_set_existant(self):
        key = self.mockapi.settings['default_settings'].keys()[0]
        value = 'new value'
        result = self.settings.set(key, value)
        self.assertIs(result, True)

        calls = [
            mock.call('settings/set_default', key=key, value=value),
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_set_multi(self):
        items = {
            self.mockapi.settings['default_settings'].keys()[0]: 'updated',
            'not_set': 'new setting',
        }
        report = self.settings.set_multi(items)
        expected = {
            self.mockapi.settings['default_settings'].keys()[0]: True,
            'not_set': False,
        }
        self.assertEqual(report, expected)

        calls = [
            mock.call('settings/set_default_multi', items=items)
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_delete(self):
        key = self.mockapi.settings['default_settings'].keys()[0]
        result = self.settings.delete(key)
        self.assertIs(result, True)

        calls = [
            mock.call('settings/delete_default', key=key)
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

if __name__ == '__main__':
    unittest.main()
