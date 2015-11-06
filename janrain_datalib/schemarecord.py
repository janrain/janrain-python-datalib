"""SchemaRecord class."""
from janrain_datalib.exceptions import ApiError
from janrain_datalib.utils import to_capture_record

class SchemaRecord(object):
    """Encapsulates a schema record."""

    def __init__(self, app, schema_name, id_value, id_attribute='uuid'):
        """Initialize.

        Args:
            app: App object
            schema_name: name of schema
            id_value: value of id_attribute
            id_attribute: attribute to use for identifying the record,
                (must have 'unique' constraint).
        """
        self._app = app
        self._schema_name = schema_name
        self._id_value = id_value
        self._id_attribute = id_attribute

    @property
    def app(self):
        """:class:`.App` object."""
        return self._app

    @property
    def schema_name(self):
        """Schema name."""
        return self._schema_name

    @property
    def id_value(self):
        """Identifier value."""
        return self._id_value

    @property
    def id_attribute(self):
        """Identifier attribute."""
        return self._id_attribute

    def as_dict(self, attributes=None):
        """The record as a dict.

        Args:
            attributes: list of attributes to include (default: all attributes)

        Returns:
            record dict
        """
        kwargs = {
            'type_name': self.schema_name,
            'key_attribute': self.id_attribute,
            # must be a "JSON" string
            'key_value': '"{}"'.format(self.id_value),
        }
        if attributes is not None:
            kwargs['attributes'] = attributes
        r = self.app.apicall('entity', **kwargs)
        return r['result']

    def validate_password(self, password, password_attribute='password'):
        """Validate the password for a record.

        Args:
            password: the password
            password_attribute: the password attribute in the schema

        Returns:
            bool
        """
        kwargs = {
            'type_name': self.schema_name,
            'key_attribute': self.id_attribute,
            # must be a "JSON" string
            'key_value': '"{}"'.format(self.id_value),
            'password_attribute': password_attribute,
            'password_value': password,
            'attributes': [self.id_attribute],
        }
        try:
            self.app.apicall('entity', **kwargs)
        except ApiError as e:
            if e.code == 350:
                return False
            raise
        return True

    def create(self, attributes, key_map=None, transform_map=None):
        """Create a new record.

        Args:
            attributes: dict of attributes and their values.
            key_map: dict that maps keys in attributes to attribute dot-paths
            transform_map: dict that maps keys in attributes to transform functions

        Returns:
            dict containing id and uuid of new record
        """
        if key_map:
            attributes = to_capture_record(attributes, key_map, transform_map)

        kwargs = {
            'type_name': self.schema_name,
            'attributes': attributes,
        }
        r = self.app.apicall('entity.create', **kwargs)
        self._id_attribute = 'uuid'
        self._id_value = r['uuid']

        return {
            'id': r['id'],
            'uuid': r['uuid'],
        }

    def delete(self):
        """Delete record."""
        kwargs = {
            'type_name': self.schema_name,
            'key_attribute': self.id_attribute,
            # must be a "JSON" string
            'key_value': '"{}"'.format(self.id_value),
        }
        self.app.apicall('entity.delete', **kwargs)

    def replace(self, attributes, attribute_path=None, key_map=None, transform_map=None):
        """Replace record.
        Warning: attributes not specified will be set to null,
            plurals not specified will be deleted.

        Args:
            attributes: dict of attributes and their values.
            attribute_path: path to a subset of record attributes to replace
            key_map: dict that maps keys in attributes to attribute dot-paths
            transform_map: dict that maps keys in attributes to transform functions
        """
        if key_map:
            attributes = to_capture_record(attributes, key_map, transform_map)

        kwargs = {
            'type_name': self.schema_name,
            'key_attribute': self.id_attribute,
            # must be a "JSON" string
            'key_value': '"{}"'.format(self.id_value),
            'attributes': attributes,
        }
        if attribute_path is not None:
            kwargs['attribute_name'] = attribute_path
        self.app.apicall('entity.replace', **kwargs)

    def update(self, attributes, attribute_path=None, key_map=None, transform_map=None):
        """Update record.

        Args:
            attributes: dict of attributes and their values.
            attribute_path: path to a subset of record attributes to update
            key_map: dict that maps keys in attributes to attribute dot-paths
            transform_map: dict that maps keys in attributes to transform functions
        """
        if key_map:
            attributes = to_capture_record(attributes, key_map, transform_map)

        kwargs = {
            'type_name': self.schema_name,
            'key_attribute': self.id_attribute,
            # must be a "JSON" string
            'key_value': '"{}"'.format(self.id_value),
            'attributes': attributes,
        }
        if attribute_path is not None:
            kwargs['attribute_name'] = attribute_path
        self.app.apicall('entity.update', **kwargs)
