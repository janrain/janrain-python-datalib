"""Tests for SchemaRecord."""
import mock
import unittest

from janrain_datalib.app import App
from janrain_datalib.schemarecord import SchemaRecord
from .mockapi import Mockapi

class TestSchemaRecord(unittest.TestCase):

    def setUp(self):
        # use a mock for the api calls
        self.mockapi = Mockapi('')

        # create the app object
        self.app = App(self.mockapi)

        self.schema_name = 'janraintestschema'

        self.uuid = '00000000-0000-0000-0000-000000000001'

        # create the entities object
        self.record = SchemaRecord(self.app, self.schema_name, self.uuid)

    def test_as_dict(self):
        record = self.record.as_dict()
        self.assertEqual(record, self.mockapi.entities[0])

        calls = [
            mock.call('entity', type_name=self.schema_name, key_attribute='uuid', key_value='"{}"'.format(self.uuid))
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_create(self):
        attributes = {
            'email': 'test@test.test'
        }
        result = self.record.create(attributes)
        self.assertEqual(result['uuid'], self.mockapi.entities[0]['uuid'])

        calls = [
            mock.call('entity.create', type_name=self.schema_name, attributes=attributes)
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_create_with_maps(self):
        record = {
            'balance': '12.00',
        }
        key_map = {
            'balance': 'wallet.balance',
        }
        transform_map = {
            'balance': lambda x: float(x),
        }
        result = self.record.create(record, key_map=key_map, transform_map=transform_map)
        self.assertEqual(result['uuid'], self.mockapi.entities[0]['uuid'])

        expected_attributes = {
            'wallet': {
                'balance': 12.00,
            },
        }
        calls = [
            mock.call('entity.create', type_name=self.schema_name, attributes=expected_attributes)
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_delete(self):
        self.record.delete()

        calls = [
            mock.call('entity.delete', type_name=self.schema_name, key_attribute='uuid', key_value='"{}"'.format(self.uuid))
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_replace(self):
        attr = {
            'email': 'test@test.test'
        }
        self.record.replace(attr)

        calls = [
            mock.call('entity.replace', type_name=self.schema_name, key_attribute='uuid', key_value='"{}"'.format(self.uuid), attributes=attr)
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_replace_with_maps(self):
        record = {
            'balance': '12.00',
        }
        key_map = {
            'balance': 'wallet.balance',
        }
        transform_map = {
            'balance': lambda x: float(x),
        }
        self.record.replace(record, key_map=key_map, transform_map=transform_map)

        expected_attributes = {
            'wallet': {
                'balance': 12.00,
            },
        }
        calls = [
            mock.call('entity.replace', type_name=self.schema_name, key_attribute='uuid', key_value='"{}"'.format(self.uuid), attributes=expected_attributes)
        ]

    def test_update(self):
        attr = {
            'email': 'test@test.test'
        }
        self.record.update(attr)

        calls = [
            mock.call('entity.update', type_name=self.schema_name, key_attribute='uuid', key_value='"{}"'.format(self.uuid), attributes=attr)
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_update_with_maps(self):
        record = {
            'balance': '12.00',
        }
        key_map = {
            'balance': 'wallet.balance',
        }
        transform_map = {
            'balance': lambda x: float(x),
        }
        self.record.update(record, key_map=key_map, transform_map=transform_map)

        expected_attributes = {
            'wallet': {
                'balance': 12.00,
            },
        }
        calls = [
            mock.call('entity.update', type_name=self.schema_name, key_attribute='uuid', key_value='"{}"'.format(self.uuid), attributes=expected_attributes)
        ]

if __name__ == '__main__':
    unittest.main()
