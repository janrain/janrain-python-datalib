"""Tests for Client."""
import mock
import unittest

from janrain_datalib.app import App
from janrain_datalib.client import Client
from janrain_datalib.clientsettings import ClientSettings
from .mockapi import Mockapi

class TestClient(unittest.TestCase):

    def setUp(self):
        # use a mock for the api calls
        self.mockapi = Mockapi('')

        # create the app object
        self.app = App(self.mockapi)

        # create the client object
        self.client_id = self.mockapi.clients_list[0]['client_id']
        self.client = Client(self.app, self.client_id)

    def test_create(self):
        description = 'client2'
        features = ['login_client']
        new_client_id = self.client.create(description, features)
        expected = self.mockapi.new_client_id
        self.assertEqual(new_client_id, expected)

        calls = [
            mock.call('clients/add', description=description, features=features),
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_delete(self):
        self.client.delete()

        calls = [
            mock.call('clients/delete', client_id_for_deletion=self.client_id)
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_reset_secret(self):
        # clients must be cached for this test to succeed
        # since the mockapi doesn't actually update the client
        # but the cache will get updated
        self.client.as_dict()  # get clients into cache

        hours_to_live = '3'
        new_client_secret = self.client.reset_secret(hours_to_live)
        expected = self.mockapi.new_client_secret
        self.assertEqual(new_client_secret, expected)

        calls = [
            mock.call('clients/list'),
            mock.call('clients/reset_secret', hours_to_live=hours_to_live, for_client_id=self.client_id)
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_set_description(self):
        description = 'new description'
        # clients must be cached for this test to succeed
        # since the mockapi doesn't actually update the client
        # but the cache will get updated
        self.client.as_dict()  # get clients into cache

        cache_key = 'clients.{}.description'.format(self.client_id)
        self.assertNotEqual(self.app.get_cache(cache_key), description)

        # set description
        self.client.set_description(description)

        # cache was updated
        self.assertEqual(self.app.get_cache(cache_key), description)

        calls = [
            mock.call('clients/list'),
            mock.call('clients/set_description', description=description, for_client_id=self.client_id),
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_set_features(self):
        features = ['test']
        # clients must be cached for this test to succeed
        # since the mockapi doesn't actually update the client
        # but the cache will get updated
        self.client.as_dict()  # get clients into cache

        cache_key = 'clients.{}.features'.format(self.client_id)
        self.assertNotEqual(self.app.get_cache(cache_key), features)

        # set features
        self.client.set_features(features)

        # cache was updated
        self.assertEqual(self.app.get_cache(cache_key), features)

        calls = [
            mock.call('clients/list'),
            mock.call('clients/set_features', features=features, for_client_id=self.client_id),
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_set_whitelist(self):
        whitelist = ['192.168.0.0/24']
        # clients must be cached for this test to succeed
        # since the mockapi doesn't actually update the client
        # but the cache will get updated
        self.client.as_dict()  # get clients into cache

        cache_key = 'clients.{}.whitelist'.format(self.client_id)
        self.assertNotEqual(self.app.get_cache(cache_key), whitelist)

        # set whitelist
        self.client.set_whitelist(whitelist)

        # cache was updated
        self.assertEqual(self.app.get_cache(cache_key), whitelist)

        calls = [
            mock.call('clients/list'),
            mock.call('clients/set_whitelist', whitelist=whitelist, for_client_id=self.client_id),
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_settings(self):
        client_settings = self.client.settings
        self.assertTrue(isinstance(client_settings, ClientSettings))

        # no api calls were made
        self.assertEqual([], self.mockapi.call.mock_calls)

    def test_as_dict(self):
        client_dict = self.client.as_dict()
        expected = self.mockapi.clients_list[0]
        self.assertEqual(client_dict, expected)

        # client is in cache
        expected = self.app.get_cache('clients')
        self.assertEqual(client_dict, expected[self.client_id])

        # modifying dict does not modify app cache
        client_dict['description'] = 'test'
        self.assertNotEqual(client_dict, expected)

if __name__ == '__main__':
    unittest.main()
