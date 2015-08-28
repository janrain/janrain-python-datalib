"""Tests for ClientSettings."""
import mock
import unittest

from janrain_datalib.app import App
from janrain_datalib.clientsettings import ClientSettings
from .mockapi import Mockapi

class TestClientSettings(unittest.TestCase):

    def setUp(self):
        # use a mock for the api calls
        self.mockapi = Mockapi('')

        # shortcuts to some values
        self.client_id = self.mockapi.clients_list[0]['client_id']
        self.client_settings = self.mockapi.settings['client_settings'][self.client_id]

        # create the app object
        self.app = App(self.mockapi)

        # create the client settings object
        self.settings = ClientSettings(self.app, self.client_id)

    def test_get_existant(self):
        # get existing setting
        key = self.client_settings.keys()[0]
        value = self.settings.get(key)
        expected = self.client_settings[key]
        self.assertEqual(value, expected)

        calls = [
            mock.call('settings/get_all'),
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

        # cache is populated
        expected = self.mockapi.settings
        self.assertEqual(self.app.get_cache('settings'), expected)

        key = self.client_settings.keys()[1]
        value = self.settings.get(key)
        expected = self.client_settings[key]
        self.assertEqual(value, expected)

        # getting another setting does not cause more api calls
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_get_nonexistant(self):
        # get setting that does not exist
        key = 'bogus'
        value = self.settings.get(key)
        self.assertIs(value, None)

        # cache is populated
        expected = self.mockapi.settings
        self.assertEqual(self.app.get_cache('settings'), expected)

        calls = [
            mock.call('settings/get_all'),
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_get_all(self):
        all_settings = self.settings.get_all()
        expected = self.mockapi.settings['default_settings']
        expected.update(self.mockapi.settings['client_settings'][self.settings.client_id])
        self.assertEqual(all_settings, expected)

        # cache is populated
        expected = self.mockapi.settings
        self.assertEqual(self.app.get_cache('settings'), expected)

        calls = [
            mock.call('settings/get_all'),
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_set(self):
        # existing key
        key = self.client_settings.keys()[0]
        value = 'new value'
        result = self.settings.set(key, value)
        self.assertIs(result, True)

        # cache is not populated
        try:
            self.app.get_cache('settings')
        except KeyError:
            pass  # expection
        else:
            self.fail("KeyError not raised on missing cache key")

        calls = [
            mock.call('settings/set', for_client_id=self.client_id, key=key, value=value),
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

        # non-existing key
        key = 'bogus'
        value = self.settings.get(key)
        self.assertIs(value, None)
        calls.append(mock.call('settings/get_all'))
        self.assertEqual(calls, self.mockapi.call.mock_calls)

        # cache is populated
        expected = self.mockapi.settings
        self.assertEqual(self.app.get_cache('settings'), expected)

        # set non-existing key
        result = self.settings.set(key, value)
        self.assertIs(result, False)

        # cache is updated
        expected = self.app.get_cache('settings.client_settings.{}.{}'.format(self.client_id, key))
        self.assertEqual(value, expected)

        calls.append(mock.call('settings/set', for_client_id=self.client_id, key=key, value=value))
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_set_multi(self):
        items = {
            self.client_settings.keys()[0]: 'updated',
            'bogus': 'new setting',
        }
        report = self.settings.set_multi(items)
        expected = {
            self.client_settings.keys()[0]: True,
            'bogus': False,
        }
        self.assertEqual(report, expected)

        # cache is not populated
        try:
            self.app.get_cache('settings')
        except KeyError:
            pass  # expection
        else:
            self.fail("KeyError not raised on missing cache key")

        calls = [
            mock.call('settings/set_multi', for_client_id=self.client_id, items=items)
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_delete(self):
        key = self.client_settings.keys()[0]
        result = self.settings.delete(key)
        self.assertIs(result, True)

        calls = [
            mock.call('settings/delete', for_client_id=self.client_id, key=key)
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

if __name__ == '__main__':
    unittest.main()
