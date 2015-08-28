"""Tests for App."""
import mock
import unittest

import janrain.capture

import janrain_datalib.exceptions
from janrain_datalib.app import App
from janrain_datalib.client import Client
from janrain_datalib.defaultsettings import DefaultSettings
from janrain_datalib.schema import Schema
from .mockapi import Mockapi

class TestApp(unittest.TestCase):

    def setUp(self):
        # use a mock for the api calls
        self.mockapi = Mockapi('')

        # create the app object to be tested
        self.app = App(self.mockapi)

    def test_apicall(self):
        args = (402, '', '', '')
        self.mockapi.call.side_effect = janrain.capture.ApiResponseError(*args)
        try:
            self.app.apicall('flows/get')
        except janrain_datalib.exceptions.ApiAuthError:
            pass  # expection
        else:
            self.fail("ApiAuthError not raised on 402 code from api")

        args = (222, '', '', '')
        self.mockapi.call.side_effect = janrain.capture.ApiResponseError(*args)
        try:
            self.app.apicall('flows/get')
        except janrain_datalib.exceptions.ApiNotFoundError:
            pass  # expection
        else:
            self.fail("ApiNotFoundError not raised on 222 code from api")

    def test_cache(self):
        # set
        self.app.set_cache('testkey', 'testvalue')
        expected = {
            'testkey': 'testvalue',
        }
        self.assertEqual(self.app.get_cache(), expected)

        # set non-existant
        self.app.set_cache('testkey.a.b', 'testvalue')
        # value was not set
        self.assertEqual(self.app.get_cache(), expected)

        # force set non-existant
        self.app.set_cache('testkey.a.b', 'testvalue', force=True)
        expected = {
            'testkey': {
                'a': {
                    'b': 'testvalue',
                }
            }
        }
        self.assertEqual(self.app.get_cache(), expected)

        # delete
        self.app.del_cache('testkey')
        self.assertEqual(self.app.get_cache(), {})

        # multi-level
        data = {
            'a': {
                'b': 'testvalue'
            }
        }
        self.app.set_cache('testkey', data)
        expected = {
            'testkey': data,
        }
        self.assertEqual(self.app.get_cache(), expected)

        # add to last level
        expected['testkey']['a']['c'] = 'test2'
        self.app.set_cache('testkey.a.c', 'test2')
        self.assertEqual(self.app.get_cache(), expected)

        # delete non-existant key - no error, no change
        self.app.del_cache('testkey.a.z')
        self.assertEqual(self.app.get_cache(), expected)

        # delete sub-level
        self.app.del_cache('testkey.a')
        expected = {
            'testkey': {}
        }
        self.assertEqual(self.app.get_cache(), expected)

        # get non-existant key
        try:
            self.app.get_cache('testkey.a.z')
        except KeyError:
            pass  # expection
        else:
            self.fail("KeyError was not raised when getting non-existant cache key")

    def test_clients_as_dict(self):
        clients = self.app.clients_as_dict()
        expected = {x['client_id']: x for x in self.mockapi.clients_list}

        self.assertEqual(clients, expected)
        calls = [
            mock.call('clients/list')
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

        clients = self.app.clients_as_dict()
        self.assertEqual(clients, expected)
        # no additional api calls were made
        self.assertEqual(calls, self.mockapi.call.mock_calls)

        # clear cache and try again
        self.app.del_cache()
        clients = self.app.clients_as_dict()
        self.assertEqual(clients, expected)
        # triggered re-fetch
        calls.append(mock.call('clients/list'))
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_settings_as_dict(self):
        settings = self.app.settings_as_dict()
        expected = self.mockapi.settings

        self.assertEqual(settings, expected)
        calls = [
            mock.call('settings/get_all')
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

        settings = self.app.settings_as_dict()
        # no additional api calls were made
        self.assertEqual(calls, self.mockapi.call.mock_calls)

        # clear cache and try again
        self.app.del_cache()
        settings = self.app.settings_as_dict()
        self.assertEqual(settings, expected)
        # triggered re-fetch
        calls.append(mock.call('settings/get_all'))
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_list_schemas(self):
        schemas = sorted(self.app.list_schemas())
        expected = sorted(self.mockapi.schemas_list)

        self.assertEqual(schemas, expected)
        calls = [
            mock.call('entityType.list')
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

        schemas = sorted(self.app.list_schemas())
        self.assertEqual(schemas, expected)
        # no additional api calls were made
        self.assertEqual(calls, self.mockapi.call.mock_calls)

        # cache was updated
        expected = {
            'schema_names': schemas,
        }
        self.assertEqual(self.app.get_cache(), expected)

        # clear cache and try again
        self.app.del_cache()
        schemas = sorted(self.app.list_schemas())
        expected = sorted(self.mockapi.schemas_list)
        self.assertEqual(schemas, expected)
        # triggered re-fetch
        calls.append(mock.call('entityType.list'))
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_default_settings(self):
        self.assertTrue(isinstance(self.app.default_settings, DefaultSettings))
        # no api calls were made
        self.assertEqual([], self.mockapi.call.mock_calls)

    def test_get_client(self):
        client_id = 'test'
        client = self.app.get_client(client_id)

        self.assertTrue(isinstance(client, Client))
        self.assertEqual(client.client_id, client_id)
        # no api calls were made
        self.assertEqual([], self.mockapi.call.mock_calls)

    def test_get_schema(self):
        schema_name = 'test'
        schema = self.app.get_schema(schema_name)

        self.assertTrue(isinstance(schema, Schema))
        # no api calls were made
        self.assertEqual([], self.mockapi.call.mock_calls)

if __name__ == '__main__':
    unittest.main()
