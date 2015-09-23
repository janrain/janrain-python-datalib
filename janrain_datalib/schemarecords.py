"""SchemaRecords class."""
import re

from janrain_datalib.utils import to_csv
from janrain_datalib.utils import dot_lookup
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

    def iterator(self, attributes=None, batch_size=100, filtering=None):
        """Iterate over entities in the schema.
        Does not allow arbitrary sorting; sorts by id in order to use it
        for paging for efficiency reasons.

        Args:
            attributes: list of attributes to include in results
                (default: all attributes)
            batch_size: max number of entities in each batch
            filtering: filter to apply (e.g., 'lastUpdated > 2000-01-01')

        Yields:
            the next entity
        """
        remove_id = False  # whether to remove id from results
        if attributes is not None and 'id' not in attributes:
            # must add id to attributes in order to get the last one
            attributes = attributes + ['id']
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
                for record in r['results']:
                    if remove_id:
                        record.pop('id', None)
                    yield record
            else:
                break

    def csv_iterator(self, attributes, batch_size=None, filtering=None, headers=True):
        """Iterate over entities in the schema and format as CSV.

        Newlines within fields will be escaped as '\\n' to ensure that each
        line contains an entire record.

        If a requested attribute is an object or plural it will be converted
        to a JSON string.

        Args:
            attributes: list of attributes to include
            batch_size: max number of entities in each batch
            filtering: filter to apply (e.g., 'lastUpdated > 2000-01-01')
            headers:
                if falsey, don't include headers
                if True, headers will be the attribute path as specified
                if a dict, then the headers will be looked up from it using the
                    attribute path - if lookup fails, fallback to using the
                    attribute path

        Yields:
            a CSV row as a string
        """
        if headers:
            if headers is True:
                headers = {}
            row = []
            for attr in attributes:
                if attr in headers:
                    row.append(headers[attr])
                else:
                    row.append(attr)
            yield to_csv(row)

        kwargs = {
            'attributes': attributes
        }
        if batch_size is not None:
            kwargs['batch_size'] = batch_size
        if filtering is not None:
            kwargs['filtering'] = filtering

        for entity in self.iterator(**kwargs):
            row = [dot_lookup(entity, attr) for attr in attributes]
            yield to_csv(row)

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
