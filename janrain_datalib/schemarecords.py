"""SchemaRecords class."""
import re

from janrain_datalib.schemarecord import SchemaRecord

class SchemaRecords(object):
    """Encapsulates the records in a schema."""

    def __init__(self, app, schema_name):
        """Initialize.

        Args:
            app: App object
            schema_name: name of schema
        """
        self._app = app
        self._schema_name = schema_name

    @property
    def app(self):
        """:class:`.App` object."""
        return self._app

    @property
    def schema_name(self):
        """Schema name."""
        return self._schema_name

    def create(self, entities, mode='smart'):
        """Create a batch of entities all at once.

        Args:
            entities: list of dicts of attribute keys and values
            mode: the mode to use when committing the batch
                options: ('smart', 'each', 'all')
                    'smart': try to create all in a single batch - if it fails,
                        fallback to 'each' (minimizes failures
                        while providing a speed boost if most entities are ok)
                    'each': create each entity separately - if one fails,
                        continue to the next one (slow)
                    'all': create all in a single batch - if any one fails, all
                        of the entities in the batch will fail (fast, but some
                        entities may fail that would not have)
        Returns:
            list of uuids for new entities or error messages for failures
        """
        if mode == 'each':
            mode = True
        elif mode == 'all':
            mode = False
        kwargs = {
            'type_name': self.schema_name,
            'all_attributes': entities,
            'commit_each': mode,
        }
        r = self.app.apicall('entity.bulkCreate', **kwargs)
        return r['uuid_results']

    def delete(self):
        """Delete all entities in the schema."""
        kwargs = {
            'type_name': self.schema_name,
            'commit': True,
        }
        self.app.apicall('entity.purge', **kwargs)

    def count(self, filtering=None):
        """Total entities in the schema.

        Args:
            filtering: filter to apply (default: count all entities)

        Returns:
            count of entities
        """
        kwargs = {
            'type_name': self.schema_name,
        }
        if filtering:
            kwargs['filter'] = filtering
        r = self.app.apicall('entity.count', **kwargs)
        return r['total_count']

    def iterator(self, batch_size=100, filtering=None, attributes=None):
        """Iterate over entities in the schema.
        Does not allow arbitrary sorting; sorts by id in order to use it
        for paging for efficiency reasons.

        Args:
            batch_size: max number of entities in each batch
            attributes: list of attributes to include in results
                (default: all attributes)
            filtering: filter to apply (e.g., 'lastUpdated > 2000-01-01')

        Yields:
            list of entities
        """
        remove_id = False  # whether to remove id from results
        if attributes is not None and 'id' not in attributes:
            # must add id to attributes in order to get the last one
            attributes.append('id')
            # but then remove it from the results because it wasn't asked for
            remove_id = True

        last_id = 0
        if filtering is None:
            filtering = 'id > {}'.format(last_id)
        else:
            filtering = '{} and id > {}'.format(filtering, last_id)
        while True:
            kwargs = {
                'type_name': self.schema_name,
                'filter': filtering,
                'sort_on': ['id'],
                'max_results': batch_size,
            }
            if attributes:
                kwargs['attributes'] = attributes
            r = self.app.apicall('entity.find', **kwargs)

            if r['results']:
                last_id = r['results'][-1]['id']
                filtering = re.sub(r'id > (\d+)', 'id > {}'.format(last_id), filtering)
                if remove_id:
                    for entity in r['results']:
                        entity.pop('id', None)
                yield r['results']
            else:
                break

    def get_record(self, id_value, id_attribute='uuid'):
        """Get a :class:`.SchemaRecord` object.

        Args:
            id_value: the value of the id_key
            id_attribute: attribute to use for identifying the record,
                (must have 'unique' constraint).

        Returns:
            SchemaRecord object
        """
        return SchemaRecord(self.app, self.schema_name, id_value, id_attribute)
