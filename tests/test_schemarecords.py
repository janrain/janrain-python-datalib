"""Tests for Schema."""
from __future__ import unicode_literals
import math
import mock
import time
import unittest
import io

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
        report = list(self.records.create(all_attributes))
        self.assertEqual(len(report), 13)
        self.assertEqual(report[0], '00000000-0000-0000-0000-000000000000')
        self.assertEqual(report[12]['stat'], 'error')

        calls = [
            mock.call(
                'entity.bulkCreate',
                type_name=self.schema_name,
                all_attributes=all_attributes,
                commit_each='smart')
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_create_batches(self):
        def record_generator(num_records):
            for i in range(num_records):
                yield {"email": "test{}@test.test".format(i)}

        num_records = 20
        batch_size = 3
        concurrency = 2
        report = list(self.records.create(
            record_generator(num_records),
            batch_size=batch_size,
            concurrency=concurrency))
        self.assertEqual(len(report), num_records)

        num_calls = math.ceil(num_records / batch_size)
        self.assertEqual(num_calls, len(self.mockapi.call.mock_calls))

    def test_create_batches_error(self):
        def record_generator(num_records):
            for i in range(num_records):
                yield {"email": "test{}@test.test".format(i)}

        def mock_call(*args, **kwargs):
            time.sleep(1)
            raise Exception('error')
        self.mockapi.call = mock.Mock(side_effect=mock_call)

        num_records = 20
        batch_size = 3
        concurrency = 2
        try:
            list(self.records.create(
                record_generator(num_records),
                batch_size=batch_size,
                concurrency=concurrency))
        except Exception:
            pass  # expection
        else:
            self.fail("Error not raised on exception")

    def test_create_each(self):
        all_attributes = [{"email": "test0@test.test"}]
        report = list(self.records.create(all_attributes, mode='each'))
        self.assertEqual(len(report), len(all_attributes))
        calls = [
            mock.call(
                'entity.bulkCreate',
                type_name=self.schema_name,
                all_attributes=all_attributes,
                commit_each=True)
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_create_all(self):
        all_attributes = [{"email": "test0@test.test"}]
        report = list(self.records.create(all_attributes, mode='all'))
        self.assertEqual(len(report), len(all_attributes))
        calls = [
            mock.call(
                'entity.bulkCreate',
                type_name=self.schema_name,
                all_attributes=all_attributes,
                commit_each=False)
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

    def test_find(self):
        kwargs = {
            'attributes': ['givenName', 'primaryAddress.city'],
            'sort_on': ['givenName'],
            'batch_size': 3,
            'start_index': 6,
            'filtering': "lastUpdated > '2001-01-01'",
        }
        records = self.records.find(**kwargs)
        self.assertEqual(len(records), kwargs['batch_size'])

        call_kwargs = {
            'type_name': self.schema_name,
            'attributes': kwargs['attributes'],
            'sort_on': kwargs['sort_on'],
            'max_results': kwargs['batch_size'],
            'first_result': kwargs['start_index'],
            'filter': kwargs['filtering'],
        }
        calls = [
            mock.call('entity.find', **call_kwargs)
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_iterator(self):
        total = 0
        batches = 1
        batch_size = 5
        entity_id = 0
        calls = []
        kwargs = {
            'type_name': self.schema_name,
            'filter': 'id > {}'.format(entity_id),
            'sort_on': ['id'],
            'max_results': 5,
        }
        calls.append(mock.call('entity.find', **kwargs))
        for i, entity in enumerate(self.records.iterator(batch_size=batch_size), start=1):
            entity_id = entity['id']
            self.assertEqual(entity_id, i)
            if i % batch_size == 0:
                kwargs['filter'] = 'id > {}'.format(entity_id)
                calls.append(mock.call('entity.find', **kwargs))
                batches += 1
            total += 1
        kwargs['filter'] = 'id > 43'
        calls.append(mock.call('entity.find', **kwargs))

        self.assertEqual(total, len(self.mockapi.entities))
        self.assertEqual(batches, math.ceil(total / float(batch_size)))

        self.assertEqual(calls, self.mockapi.call.mock_calls)

    def test_csv_iterator(self):
        csv_file = io.StringIO(newline=None)
        attributes = ['uuid', 'email', 'address.city', 'aboutMe', 'lastUpdated', 'adlists']
        for record in self.records.csv_iterator(attributes):
            csv_file.write(record)
        from .mockapi import load_file
        expected = load_file('test_csv_iterator.csv')
        self.assertEqual(csv_file.getvalue(), expected)

    def test_get_record(self):
        record = self.records.get_record('')
        self.assertTrue(isinstance(record, SchemaRecord))

        # no calls were made
        self.assertEqual([], self.mockapi.call.mock_calls)

if __name__ == '__main__':
    unittest.main()
