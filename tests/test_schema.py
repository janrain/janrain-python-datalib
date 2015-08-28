"""Tests for Schema."""
import mock
import unittest

from janrain_datalib.app import App
from janrain_datalib.schemarecords import SchemaRecords
from janrain_datalib.schema import Schema
from .mockapi import Mockapi

class TestSchema(unittest.TestCase):

    def setUp(self):
        # use a mock for the api calls
        self.mockapi = Mockapi('')

        # create the app object
        self.app = App(self.mockapi)

        self.schema_name = 'janraintestschema'

        # create the schema object
        self.schema = Schema(self.app, self.schema_name)

    def test_create_delete(self):
        attr_defs = []
        new_attr_defs = self.schema.create(attr_defs)
        self.assertEqual(new_attr_defs, attr_defs)

        calls = [
            mock.call('entityType.create', type_name=self.schema_name, attr_defs=attr_defs)
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

        # cache updated
        expected = {
            'schemas': {
                self.schema_name: {
                    'attr_defs': attr_defs,
                }
            }
        }
        self.assertEqual(self.app.get_cache(), expected)

        self.schema.delete()

        calls.append(mock.call('entityType.properties', type_name=self.schema_name))
        for prop in self.mockapi.schema_properties:
            calls.append(mock.call('entityType.removeProperty', type_name=self.schema_name, uuid=prop['uuid']))
        calls.append(mock.call('entityType.delete', type_name=self.schema_name, commit=True))
        self.assertEqual(calls, self.mockapi.call.mock_calls)

        # cache updated
        expected = {
            'schemas': {}
        }
        self.assertEqual(self.app.get_cache(), expected)

    def test_add_attribute(self):
        attr_def = {
            'name': 'test',
            'type': 'test',
        }
        self.schema.add_attribute(attr_def)

        calls = [
            mock.call('entityType.addAttribute', type_name=self.schema_name, attr_def=attr_def),
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

        # cache updated
        expected = {
            'schemas': {
                self.schema_name: {
                    'attr_defs': self.mockapi.schema_attributes,
                }
            }
        }
        self.assertEqual(self.app.get_cache(), expected)

    def test_remove_attribute(self):
        attr_name = 'aboutMe'
        self.schema.remove_attribute(attr_name)

        calls = [
            mock.call('entityType.removeAttribute', type_name=self.schema_name, attribute_name=attr_name),
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

        # cache updated
        expected = {
            'schemas': {
                self.schema_name: {
                    'attr_defs': self.mockapi.schema_attributes,
                }
            }
        }
        self.assertEqual(self.app.get_cache(), expected)

    def test_set_attribute_description(self):
        attr_name = 'aboutMe'
        description = 'test description'
        self.schema.set_attribute_description(attr_name, description)

        calls = [
            mock.call('entityType.setAttributeDescription', type_name=self.schema_name, attribute_name=attr_name, description='"{}"'.format(description))
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

        # cache updated
        expected = {
            'schemas': {
                self.schema_name: {
                    'attr_defs': self.mockapi.schema_attributes,
                }
            }
        }
        self.assertEqual(self.app.get_cache(), expected)

    def test_set_attribute_constraints(self):
        attr_name = 'aboutMe'
        constraints = ["new", "constraints", "list"]
        self.schema.set_attribute_constraints(attr_name, constraints)

        calls = [
            mock.call('entityType.setAttributeConstraints', type_name=self.schema_name, attribute_name=attr_name, constraints=constraints)
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

        # cache updated
        expected = {
            'schemas': {
                self.schema_name: {
                    'attr_defs': self.mockapi.schema_attributes,
                }
            }
        }
        self.assertEqual(self.app.get_cache(), expected)

    def test_add_rule(self):
        rule_def = {
            'attributes': ['aboutMe'],
            'definition': 'required',
            'description': 'test rule',
        }
        self.schema.add_rule(rule_def)

        prop_def = {
            'attributes': rule_def['attributes'],
            'type': 'rule',
            'definition': rule_def['definition'],
            'description': rule_def['description'],
        }
        calls = [
            mock.call('entityType.addProperty', type_name=self.schema_name, property=prop_def),
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

        # cache not updated
        self.assertEqual(self.app.get_cache(), {})

    def test_remove_rule(self):
        uuid = self.mockapi.schema_properties[0]['uuid']
        self.schema.remove_rule(uuid)

        calls = [
            mock.call('entityType.removeProperty', type_name=self.schema_name, uuid=uuid),
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

        # cache not updated
        self.assertEqual(self.app.get_cache(), {})

    def test_get_attr_defs(self):
        attr_defs = self.schema.get_attr_defs()
        expected = self.mockapi.schema_attributes
        self.assertEqual(attr_defs, expected)

        calls = [
            mock.call('entityType', type_name=self.schema_name, remove_reserved=False),
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

        # cache updated
        expected = {
            'schemas': {
                self.schema_name: {
                    'attr_defs': self.mockapi.schema_attributes,
                }
            }
        }
        self.assertEqual(self.app.get_cache(), expected)

    def test_get_attr_defs_remove_reserved(self):
        attr_defs = self.schema.get_attr_defs(remove_reserved=True)
        # mockapi doesn't actually remove reserved attributes
        expected = self.mockapi.schema_attributes
        self.assertEqual(attr_defs, expected)

        calls = [
            mock.call('entityType', type_name=self.schema_name, remove_reserved=True),
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

        # cache not updated
        self.assertEqual(self.app.get_cache(), {})

    def test_get_attr(self):
        attr_name = '/address/street'
        attr = self.schema.get_attr(attr_name)
        expected = {
            "name": "/address/street",
            "type": "string",
            "length": None,
            "case-sensitive": False
        }
        self.assertEqual(attr, expected)

        calls = [
            mock.call('entityType', type_name=self.schema_name, remove_reserved=False),
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

        # cache updated
        expected = {
            'schemas': {
                self.schema_name: {
                    'attr_defs': self.mockapi.schema_attributes,
                }
            }
        }
        self.assertEqual(self.app.get_cache(), expected)

    def test_get_rule_defs(self):
        rules = self.schema.get_rule_defs()
        expected = [
            {
                "attributes": [
                    "/birthday"
                ],
                "uuid": "00000000-0000-0000-0000-000000000001",
                "description": "birthday is read-only",
                "definition": "ignore-update"
            },
            {
                "attributes": [
                    "/aboutMe"
                ],
                "uuid": "00000000-0000-0000-0000-000000000002",
                "description": None,
                "definition": {
                    "truncate": 100
                }
            },
            {
                "attributes": [
                    "/givenName",
                    "/familyName"
                ],
                "uuid": "00000000-0000-0000-0000-000000000003",
                "description": "full name must be unique",
                "definition": "unique"
            }
        ]
        self.assertEqual(rules, expected)

        calls = [
            mock.call('entityType.properties', type_name=self.schema_name)
        ]
        self.assertEqual(calls, self.mockapi.call.mock_calls)

        # cache updated
        expected = {
            'schemas': {
                self.schema_name: {
                    'rules': rules
                }
            }
        }
        self.assertEqual(self.app.get_cache(), expected)

    def test_get_rule(self):
        uuid = self.mockapi.schema_properties[0]['uuid']
        rule_def = self.schema.get_rule(uuid)

        self.assertEqual(rule_def['uuid'], uuid)
        self.assertEqual(rule_def['definition'], self.mockapi.schema_properties[0]['definition'])

    def test_records(self):
        records = self.schema.records
        self.assertTrue(isinstance(records, SchemaRecords))

        # no api calls were made
        self.assertEqual([], self.mockapi.call.mock_calls)

if __name__ == '__main__':
    unittest.main()
