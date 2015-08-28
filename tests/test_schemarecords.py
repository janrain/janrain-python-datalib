"""Tests for Schema."""
import math
import mock
import unittest

from janrain_datalib.app import App
from janrain_datalib.schemarecords import SchemaRecords
from janrain_datalib.schemarecord import SchemaRecord
from .mockapi import Mockapi

class TestSchemaRecords(unittest.TestCase):

    def setUp(self):
        # use a mock for the api calls
        self.mockapi = Mockapi('')

        # create the app object
        self.app = App(self.mockapi)

        self.schema_name = 'janraintestschema'

        # create the records object
        self.records = SchemaRecords(self.app, self.schema_name)

    def test_create(self):
        all_attributes = [{"email": "test{}@test.test".format(i)} for i in range(13)]
        report = self.records.create(all_attributes)
        self.assertEqual(len(report), 13)
        self.assertEqual(report[0], '00000000-0000-0000-0000-000000000000')
        self.assertEqual(report[12]['stat'], 'error')

        calls = [
            mock.call('entity.bulkCreate', type_name=self.schema_name, all_attributes=all_attributes, commit_each='smart')
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_create_each(self):
        all_attributes = [{"email": "test0@test.test"}]
        self.records.create(all_attributes, mode='each')
        calls = [
            mock.call('entity.bulkCreate', type_name=self.schema_name, all_attributes=all_attributes, commit_each=True)
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_create_all(self):
        all_attributes = [{"email": "test0@test.test"}]
        self.records.create(all_attributes, mode='all')
        calls = [
            mock.call('entity.bulkCreate', type_name=self.schema_name, all_attributes=all_attributes, commit_each=False)
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_delete(self):
        self.records.delete()

        calls = [
            mock.call('entity.purge', type_name=self.schema_name, commit=True)
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_count(self):
        count = self.records.count()
        self.assertEqual(count, len(self.mockapi.entities))

        calls = [
            mock.call('entity.count', type_name=self.schema_name)
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_iterator(self):
        total = 0
        batches = 0
        calls = []
        for batch in self.records.iterator(batch_size=5):
            kwargs = {
                'type_name': self.schema_name,
                'filter': 'id > {}'.format(total),
                'sort_on': ['id'],
                'max_results': 5,
            }
            calls.append(mock.call('entity.find', **kwargs))
            self.assertEqual(batch[0]['id'], total+1)
            total += len(batch)
            batches += 1
        kwargs['filter'] = 'id > 43'
        calls.append(mock.call('entity.find', **kwargs))

        self.assertEqual(total, len(self.mockapi.entities))
        self.assertEqual(batches, math.ceil(total / 5.0))

        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_get_record(self):
        record = self.records.get_record('')
        self.assertTrue(isinstance(record, SchemaRecord))

        # no calls were made
        self.assertEqual([], self.mockapi.call.mock_calls)

if __name__ == '__main__':
    unittest.main()
