"""Schema class."""
from janrain_datalib.exceptions import InputError
from janrain_datalib.schemarecords import SchemaRecords
from janrain_datalib.schemaattributes import SchemaAttributes
from janrain_datalib.schemarules import SchemaRules

class Schema(object):
    """Encapsulates a schema (entityType)."""

    def __init__(self, app, name):
        """Initialize.

        Args:
            app: App object
            name: schema name
        """
        self._app = app
        self._name = name
        self._records = SchemaRecords(app, name)

    @property
    def app(self):
        """:class:`.App` object."""
        return self._app

    @property
    def name(self):
        """Schema name."""
        return self._name

    @property
    def records(self):
        """:class:`.SchemaRecords` object."""
        return self._records

    def create(self, attr_defs):
        """Create a new schema.

        Args:
            attr_defs: list of attribute definitions

        Returns:
            SchemaAttributes list
        """
        kwargs = {
            'type_name': self.name,
            'attr_defs': attr_defs,
        }
        r = self.app.apicall('entityType.create', **kwargs)
        attr_defs = SchemaAttributes(r['schema']['attr_defs'])

        # update cache
        cache_key = 'schemas.{}.attr_defs'.format(self.name)
        self.app.set_cache(cache_key, attr_defs, force=True)
        try:
            cache_key = 'schema_names'
            names = self.app.get_cache(cache_key)
            # do not use append
            names = names + [self.name]
            self.app.set_cache(cache_key, names)
        except KeyError:
            pass

        return attr_defs

    def delete(self):
        """Delete schema."""
        rules = self.get_rule_defs()
        if rules:
            # rules are not automatically deleted (unlike records)
            # so they must be deleted manually
            for rule in rules:
                self.remove_rule(rule['uuid'])

        # delete attributes and data
        kwargs = {
            'type_name': self.name,
            'commit': True,
        }
        self.app.apicall('entityType.delete', **kwargs)

        # remove from cache
        cache_key = 'schemas.{}'.format(self.name)
        self.app.del_cache(cache_key)
        try:
            cache_key = 'schema_names'
            names = self.app.get_cache(cache_key)
            names = [x for x in names if x != self.name]
            self.app.set_cache(cache_key, names)
        except KeyError:
            pass

    def add_attribute(self, attr_def):
        """Add an attribute to the schema.

        Args:
            attr_def: attribute definition

        Returns:
            updated SchemaAttributes list
        """
        try:
            attr_def['name']
        except KeyError:
            raise InputError("missing name")
        try:
            attr_def['type']
        except KeyError:
            raise InputError("missing type")

        kwargs = {
            'type_name': self.name,
            'attr_def': attr_def,
        }
        r = self.app.apicall('entityType.addAttribute', **kwargs)
        attr_defs = SchemaAttributes(r['schema']['attr_defs'])

        # update cache
        cache_key = 'schemas.{}.attr_defs'.format(self.name)
        self.app.set_cache(cache_key, attr_defs, force=True)

        return attr_defs

    def remove_attribute(self, attr_name):
        """Delete an attribute from the schema.

        Args:
            attr_name: attribute name/path

        Returns:
            updated SchemaAttributes list
        """
        kwargs = {
            'type_name': self.name,
            'attribute_name': attr_name,
        }
        r = self.app.apicall('entityType.removeAttribute', **kwargs)
        attr_defs = SchemaAttributes(r['schema']['attr_defs'])

        # update cache
        cache_key = 'schemas.{}.attr_defs'.format(self.name)
        self.app.set_cache(cache_key, attr_defs, force=True)

        return attr_defs

    def set_attribute_description(self, attr_name, description):
        """Update an attribute's description.

        Args:
            attr_name: attribute name/path
            description: attribute description

        Returns:
            updated SchemaAttributes list
        """
        kwargs = {
            'type_name': self.name,
            'attribute_name': attr_name,
            # description must be a "JSON" string
            'description': '"{}"'.format(description),
        }
        r = self.app.apicall('entityType.setAttributeDescription', **kwargs)
        attr_defs = SchemaAttributes(r['schema']['attr_defs'])

        # update cache
        cache_key = 'schemas.{}.attr_defs'.format(self.name)
        self.app.set_cache(cache_key, attr_defs, force=True)

        return attr_defs

    def set_attribute_constraints(self, attr_name, constraints):
        """Set contraints for an attribute.

        Args:
            attr_name: attribute name/path
            constraints: list of constraints to set

        Returns:
            updated SchemaAttributes list
        """
        kwargs = {
            'type_name': self.name,
            'attribute_name': attr_name,
            'constraints': constraints,
        }
        r = self.app.apicall('entityType.setAttributeConstraints', **kwargs)
        attr_defs = SchemaAttributes(r['schema']['attr_defs'])

        # update cache
        cache_key = 'schemas.{}.attr_defs'.format(self.name)
        self.app.set_cache(cache_key, attr_defs, force=True)

        return attr_defs

    def add_rule(self, rule_def):
        """Add a rule to the schema.

        Args:
            rule_def: rule definition

        Returns:
            uuid of new rule
        """
        try:
            attributes = rule_def['attributes']
        except KeyError:
            raise InputError("missing attributes list")
        try:
            definition = rule_def['definition']
        except KeyError:
            try:
                definition = rule_def['property']
            except KeyError:
                raise InputError("missing definition")

        property_def = {
            'attributes': attributes,
        }

        if definition == 'unique':
            # special case for 'unique' property
            property_def['type'] = definition
        else:
            property_def['type'] = 'rule'
            property_def['definition'] = definition

        if 'description' in rule_def and rule_def['description']:
            property_def['description'] = rule_def['description']

        kwargs = {
            'type_name': self.name,
            'property': property_def,
        }
        r = self.app.apicall('entityType.addProperty', **kwargs)
        uuid = r['result']['uuid']
        attributes = r['result']['attributes']
        definition = r['result'].get('definition', r['result'].get('property'))

        # sanitize rule_def
        rule_def = {
            'attributes': attributes,
            'definition': definition,
            'description': r['result'].get('description', None),
            'uuid': uuid,
        }

        # update cache
        cache_key = 'schemas.{}.rules'.format(self.name)
        try:
            rules = self.app.get_cache(cache_key)
            # do not use append
            rules = rules + [rule_def]
            self.app.set_cache(cache_key, rules)
        except KeyError:
            pass

        return uuid

    def remove_rule(self, uuid):
        """Delete a rule from the schema.

        Args:
            uuid: uuid of rule to delete
        """
        kwargs = {
            'type_name': self.name,
            'uuid': uuid,
        }
        self.app.apicall('entityType.removeProperty', **kwargs)

        # remove from cache
        cache_key = 'schemas.{}.rules'.format(self.name)
        try:
            rules = self.app.get_cache(cache_key)
            rules = [x for x in rules if x['uuid'] != uuid]
            self.app.set_cache(cache_key, rules)
        except KeyError:
            pass

    def get_attr_defs(self, remove_reserved=False):
        """The raw schema attributes list.

        Args:
            remove_reserved: whether reserved attributes will be removed
                (default: False)

        Returns:
            SchemaAttributes list
        """
        cache_key = 'schemas.{}.attr_defs'.format(self.name)
        try:
            attr_defs = self.app.get_cache(cache_key)
        except KeyError:
            attr_defs = None
        if attr_defs is None or remove_reserved:
            kwargs = {
                'type_name': self.name,
                'remove_reserved': remove_reserved,
            }
            r = self.app.apicall('entityType', **kwargs)
            attr_defs = SchemaAttributes(r['schema']['attr_defs'])

            if remove_reserved:
                # do not cache attr_defs if remove_reserved is True
                return attr_defs

            # update cache
            self.app.set_cache(cache_key, attr_defs, force=True)

        return attr_defs

    def get_attr(self, attr_name):
        """Get a single attribute.
        The attr_name can be slash (/) delimited or dot (.) delimited:
        e.g.: /primaryAddress/city, profiles.profile.email

        Args:
            attr_name: attribute name/path

        Returns:
            attribute definition

        Raises:
            NotFoundError: if attribute is not found
        """
        attr_defs = self.get_attr_defs()
        attr = attr_defs.find(attr_name).copy()
        attr['name'] = attr_name
        return attr

    def get_rule_defs(self):
        """Raw rules/properties with definitions normalized.

        Returns:
            rules list
        """
        cache_key = 'schemas.{}.rules'.format(self.name)
        try:
            rules = self.app.get_cache(cache_key)
        except KeyError:
            kwargs = {'type_name': self.name}
            r = self.app.apicall('entityType.properties', **kwargs)
            properties = r['results']

            rules = SchemaRules()
            for prop in properties:
                rule = {
                    'attributes': prop['attributes'],
                    'definition': prop.get('definition', prop['property']),
                    'description': prop.get('description', None),
                    'uuid': prop['uuid'],
                }
                rules.append(rule)

            # update cache
            self.app.set_cache(cache_key, rules, force=True)

        return rules

    def get_rule(self, uuid):
        """Get a single rule.

        Args:
            uuid: uuid of rule

        Returns:
            rule definition

        Raises:
            NotFoundError: if rule is not found
        """
        rules = self.get_rule_defs()
        return rules.find(uuid)
