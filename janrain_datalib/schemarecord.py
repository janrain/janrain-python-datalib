"""SchemaRecord class."""
from janrain_datalib.exceptions import ApiError

class SchemaRecord(object):
    """Encapsulates a schema record."""

    def __init__(self, app, schema_name, id_value, id_attribute='uuid'):
        """Initialize.

        Args:
            app: App object
            schema_name: name of schema
            id_value: value of id_attribute
            id_attribute: attribute to use for identifying the entity,
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
        """The entity as a dict.

        Args:
            attributes: list of attributes to include (default: all attributes)

        Returns:
            entity dict
        """
        kwargs = {
            'type_name': self.schema_name,
            'key_attribute': self.id_attribute,
            'key_value': self.id_value,
        }
        if attributes is not None:
            kwargs['attributes'] = attributes
        r = self.app.apicall('entity', **kwargs)
        return r['result']

    def validate_password(self, password, password_attribute='password'):
        """Validate the password for an entity.

        Args:
            password: the password
            password_attribute: the password attribute in the schema

        Returns:
            bool
        """
        kwargs = {
            'type_name': self.schema_name,
            'key_attribute': self.id_attribute,
            'key_value': self.id_value,
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

    def create(self, attributes):
        """Create a new entity.

        Args:
            attributes: dict of attributes and their values.

        Returns:
            dict containing id and uuid of new entity
        """
        kwargs = {
            'type_name': self.schema_name,
            'attributes': attributes,
        }
        r = self.app.apicall('entity.create', **kwargs)

        return {
            'id': r['id'],
            'uuid': r['uuid'],
        }

    def delete(self):
        """Delete entity."""
        kwargs = {
            'type_name': self.schema_name,
            'key_attribute': self.id_attribute,
            'key_value': self.id_value,
        }
        self.app.apicall('entity.delete', **kwargs)

    def replace(self, attributes, attribute_path=None):
        """Replace entity.
        Warning: attributes not specified will be set to null,
            plurals not specified will be deleted.

        Args:
            attributes: dict of attributes and their values.
            attribute_path: path to a subset of entity attributes to replace
        """
        kwargs = {
            'type_name': self.schema_name,
            'key_attribute': self.id_attribute,
            'key_value': self.id_value,
            'attributes': attributes,
        }
        if attribute_path is not None:
            kwargs['attribute_name'] = attribute_path
        self.app.apicall('entity.replace', **kwargs)

    def update(self, attributes, attribute_path=None):
        """Update entity.

        Args:
            attributes: dict of attributes and their values.
            attribute_path: path to a subset of entity attributes to update
        """
        kwargs = {
            'type_name': self.schema_name,
            'key_attribute': self.id_attribute,
            'key_value': self.id_value,
            'attributes': attributes,
        }
        if attribute_path is not None:
            kwargs['attribute_name'] = attribute_path
        self.app.apicall('entity.update', **kwargs)
