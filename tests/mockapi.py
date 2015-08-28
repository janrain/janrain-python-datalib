"""Mock of janrain.capture.Api

Notes:
Changes to schema attributes are not reflected in the response.
"""
import copy
import json
import os
import re

import mock
import janrain.capture

def load_file(filename, subdir='data'):
    """read in a file relative to the current file's dir"""
    d = os.path.dirname(os.path.realpath(__file__))
    f = os.path.join(d, subdir, filename)
    with open(f) as fp:
        contents = fp.read()
    return contents

def load_text_file(filename, subdir='data'):
    """read in a utf-8 encoded text file relative to the current file's dir"""
    return load_file(filename, subdir=subdir).decode('utf-8')

def load_json_file(filename, subdir='data'):
    """read in a utf-8 json file relative to the current file's dir"""
    contents = load_text_file(filename, subdir=subdir)
    return json.loads(contents)

def format_json(data):
    """format data into a utf-8 encoded json string"""
    out = json.dumps(data, ensure_ascii=False, indent=4, separators=(',', ': '), sort_keys=True)
    return out.encode('utf-8')

class Mockapi(janrain.capture.Api):
    """Mock of janrain.capture.Api"""

    def __init__(self, *args, **kwargs):
        super(Mockapi, self).__init__(*args, **kwargs)
        self.clients_list = load_json_file('mockclients.json')
        self.new_client_id = "abcdefghijklmnopqrstuvwxyz987654"
        self.new_client_secret = "987654abcdefghijklmnopqrstuvwxyz"

        self.settings = load_json_file('mocksettings.json')

        self.schema_name = "janraintestschema"
        self.schema_attributes = load_json_file('mockschema.json')
        self.schema_properties = load_json_file('mockschemaproperties.json')
        self.schemas_list = [
            self.schema_name,
            "user"
        ]

        self.entities = load_json_file('mockentities.json')

        def call_side_effect(cmd, **kwargs):
            """defines the return values for various api calls"""

            ### clients ###
            if cmd == "clients/list":
                return {
                    "stat": "ok",
                    "results": copy.deepcopy(self.clients_list)
                }
            elif cmd == "clients/add":
                return {
                    "stat": "ok",
                    "description": kwargs['description'],
                    "client_id": self.new_client_id,
                    "client_secret": self.new_client_secret,
                    "features": kwargs.get('features', []),
                    "whitelist": ["0.0.0.0/0"]
                }
            elif cmd == "clients/delete":
                return {
                    "stat": "ok"
                }
            elif cmd == "clients/set_description":
                return {
                    "stat": "ok"
                }
            elif cmd == "clients/set_features":
                return {
                    "stat": "ok"
                }
            elif cmd == "clients/set_whitelist":
                return {
                    "stat": "ok"
                }
            elif cmd == "clients/reset_secret":
                return {
                    "stat": "ok",
                    "new_secret": self.new_client_secret
                }

            ### settings ###
            elif cmd == "settings/get":
                val = self.settings['client_settings'].get(kwargs['for_client_id'], {}).get(kwargs['key'], None)
                return {
                    "stat": "ok",
                    "result": val
                }
            elif cmd == "settings/get_multi":
                vals = {}
                for k in kwargs['keys']:
                    vals[k] = self.settings['client_settings'].get(kwargs['for_client_id'], {}).get(k, None)
                return {
                    "stat": "ok",
                    "result": vals
                }
            elif cmd == "settings/get_default":
                val = self.settings['default_settings'].get(kwargs['key'])
                return {
                    "stat": "ok",
                    "result": val
                }
            elif cmd == "settings/get_all":
                return {
                    "client_settings": copy.deepcopy(self.settings['client_settings']),
                    "default_settings": copy.deepcopy(self.settings['default_settings']),
                    "stat": "ok"
                }
            elif cmd == "settings/items":
                items = self.settings['default_settings'].copy()
                items.update(self.settings['client_settings'][kwargs['for_client_id']].copy())
                return {
                    "stat": "ok",
                    "result": items
                }
            elif cmd == "settings/set":
                result = True if self.settings['client_settings'].get(kwargs['for_client_id'], {}).get(kwargs['key']) else False
                return {
                    "stat": "ok",
                    "result": result
                }
            elif cmd == "settings/set_multi":
                result = {}
                for k in kwargs['items']:
                    result[k] = True if self.settings['client_settings'].get(kwargs['for_client_id'], {}).get(k) else False
                return {
                    "stat": "ok",
                    "result": result
                }
            elif cmd == "settings/set_default":
                result = True if self.settings['default_settings'].get(kwargs['key']) else False
                return {
                    "stat": "ok",
                    "result": result
                }
            elif cmd == "settings/set_default_multi":
                result = {}
                for k in kwargs['items']:
                    result[k] = True if self.settings['default_settings'].get(k) else False
                return {
                    "stat": "ok",
                    "result": result
                }
            elif cmd == "settings/delete":
                result = True if self.settings['client_settings'].get(kwargs['for_client_id'], {}).get(kwargs['key']) else False
                return {
                    "stat": "ok",
                    "result": result
                }
            elif cmd == "settings/delete_default":
                result = True if self.settings['default_settings'].get(kwargs['key']) else False
                return {
                    "stat": "ok",
                    "result": result
                }

            ### entityType ###
            elif cmd == "entityType.list":
                return {
                    "stat": "ok",
                    "results": copy.deepcopy(self.schemas_list)
                }
            elif cmd == "entityType":
                return {
                    "stat": "ok",
                    "schema": {
                        "attr_defs": copy.deepcopy(self.schema_attributes),
                        "name": kwargs['type_name']
                    }
                }
            elif cmd == "entityType.create":
                return {
                    "stat": "ok",
                    "schema": {
                        "attr_defs": kwargs['attr_defs'],
                        "name": kwargs['type_name']
                    }
                }
            elif cmd == "entityType.delete":
                return {
                    "stat": "ok"
                }
            elif cmd == "entityType.addAttribute":
                return {
                    "stat": "ok",
                    "schema": {
                        "attr_defs": copy.deepcopy(self.schema_attributes),
                        "name": kwargs['type_name']
                    }
                }
            elif cmd == "entityType.removeAttribute":
                return {
                    "stat": "ok",
                    "schema": {
                        "attr_defs": copy.deepcopy(self.schema_attributes),
                        "name": kwargs['type_name']
                    }
                }
            elif cmd == "entityType.setAttributeConstraints":
                return {
                    "stat": "ok",
                    "schema": {
                        "attr_defs": copy.deepcopy(self.schema_attributes),
                        "name": kwargs['type_name']
                    }
                }
            elif cmd == "entityType.setAttributeDescription":
                return {
                    "stat": "ok",
                    "schema": {
                        "attr_defs": copy.deepcopy(self.schema_attributes),
                        "name": kwargs['type_name']
                    }
                }
            elif cmd == "entityType.properties":
                return {
                    "stat": "ok",
                    "results": copy.deepcopy(self.schema_properties)
                }
            elif cmd == "entityType.addProperty":
                prop = kwargs['property'].copy()
                prop['uuid'] = "00000000-0000-0000-0000-000000000003"
                return {
                    "stat": "ok",
                    "result": prop
                }
            elif cmd == "entityType.removeProperty":
                return {
                    "stat": "ok"
                }
            elif cmd == "entityType.rules":
                rules = [r.copy() for r in self.schema_properties if r['property'] == 'rule']
                return {
                    "stat": "ok",
                    "results": rules
                }
            elif cmd == "entityType.addRule":
                rule = {
                    "attributes": kwargs['attributes'],
                    "definition": json.loads(kwargs['definition']),
                    "uuid": "00000000-0000-0000-0000-000000000003"
                }
                if 'description' in kwargs:
                    rule['description'] = kwargs['description']
                return {
                    "stat": "ok",
                    "result": rule
                }
            elif cmd == "entityType.removeRule":
                return {
                    "stat": "ok"
                }

            ### entity ###
            elif cmd == "entity":
                return {
                    "result": self.entities[0],
                    "stat": "ok"
                }
            elif cmd == "entity.create":
                return {
                    "id": 1,
                    "uuid": "00000000-0000-0000-0000-000000000001",
                    "stat": "ok"
                }
            elif cmd == "entity.delete":
                return {
                    "stat": "ok"
                }
            elif cmd == "entity.purge":
                return {
                    "stat": "ok"
                }
            elif cmd == "entity.count":
                return {
                    "stat": "ok",
                    "total_count": len(self.entities)
                }
            elif cmd == "entity.find":
                if 'max_results' not in kwargs:
                    kwargs['max_results'] = 100
                min_id = 0
                if 'filter' in kwargs:
                    found = re.search(r'id > (\d+)', kwargs['filter'])
                    if found:
                        min_id = int(found.group(1))
                results = []
                count = 0
                for entity in self.entities:
                    if entity['id'] > min_id:
                        results.append(entity)
                        count += 1
                        if count >= kwargs['max_results']:
                            break
                return {
                    "result_count": len(results),
                    "results": results,
                    "stat": "ok"
                }
            elif cmd == "entity.replace":
                return {
                    "stat": "ok"
                }
            elif cmd == "entity.update":
                return {
                    "stat": "ok"
                }
            elif cmd == "entity.bulkCreate":
                results = []
                uuid_results = []
                for i, entity in enumerate(kwargs['all_attributes'], start=1):
                    # make every 13th record fail
                    if i % 13 == 0:
                        err = {
                            "code": 361,
                            "error": "unique_violation",
                            "error_description": "Attempted to update a duplicate value",
                            "stat": "error"
                        }
                        results.append(err)
                        uuid_results.append(err)
                    else:
                        new_id = len(self.entities) + i
                        results.append(new_id)
                        uuid_results.append('00000000-0000-0000-0000-000000000000')
                return {
                    "results": results,
                    "uuid_results": uuid_results,
                    "stat": "ok"
                }

            else:
                raise NotImplementedError("not implemented")

        # replace the call method with a mock
        self.call = mock.Mock(side_effect=call_side_effect)
