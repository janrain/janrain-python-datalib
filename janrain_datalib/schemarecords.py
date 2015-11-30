"""SchemaRecords class."""
import json
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

    def create(self, records, mode='smart', batch_size=None):
        """Create multiple records.

        Args:
            records: list or iterator of dicts of attribute keys and values
            mode: the mode to use when committing the batch
                options: ('smart', 'each', 'all')
                    'smart': try to create all in a single batch - if it fails,
                        fallback to 'each' (minimizes failures
                        while providing a speed boost if most records are ok)
                    'each': create each record separately - if one fails,
                        continue to the next one (slow)
                    'all': create all in a single batch - if any one fails, all
                        of the records in the batch will fail (fast, but some
                        records may fail that would not have)
            batch_size: if specified, api calls will be broken up into batches
                of this number of records

        Yields:
            list of uuids for new records or errors for failures
        """
        if mode == 'each':
            mode = True
        elif mode == 'all':
            mode = False

        def create_batch(batch):
            """send batch to api"""
            kwargs = {
                'type_name': self.schema_name,
                'commit_each': mode,
                'all_attributes': batch,
            }
            r = self.app.apicall('entity.bulkCreate', **kwargs)
            return r['uuid_results']

        batch = []
        for record in records:
            batch.append(record)
            if not batch_size:
                # find reasonable batch size based on size of first record
                record_len = len(json.dumps(record))
                # limit batches to approx 1MB
                batch_size = 1 + int(1000000 / record_len)
                if batch_size > 2000:
                    # or 2000 records, whichever is less
                    batch_size = 2000
            if len(batch) >= batch_size:
                for item in create_batch(batch):
                    yield item
                batch = []
        # leftover records
        if batch:
            for item in create_batch(batch):
                yield item

    def delete(self):
        """Delete all records in the schema."""
        kwargs = {
            'type_name': self.schema_name,
            'commit': True,
        }
        self.app.apicall('entity.purge', **kwargs)

    def count(self, filtering=None):
        """Total records in the schema.

        Args:
            filtering: filter to apply (default: count all records)

        Returns:
            count of records
        """
        kwargs = {
            'type_name': self.schema_name,
        }
        if filtering:
            kwargs['filter'] = filtering
        r = self.app.apicall('entity.count', **kwargs)
        return r['total_count']

    def find(self, attributes=None, sort_on=None, batch_size=None, start_index=None, filtering=None):
        """Get a batch of records from the schema.

        Args:
            attributes: list of attributes to return in each record
                (default: all attributes)
            sort_on: list of attributes to sort by; to sort in descending order,
                prefix the attribute with a minus sign (-)
            batch_size: maximum results to return; cannot be higher than 10000
            start_index: start batch at a number other than 1;
                use this if all records cannot be returned in a single batch
            filtering: filter to apply when fetching records;
                values must be enclosed in single quotes unless they are
                attributes or integers (e.g., "lastUpdated > '2000-01-01'")

        Returns:
            list of records
        """
        kwargs = {
            'type_name': self.schema_name,
        }
        if attributes is not None:
            kwargs['attributes'] = attributes
        if sort_on is not None:
            kwargs['sort_on'] = sort_on
        if filtering is not None:
            kwargs['filter'] = filtering
        if batch_size is not None:
            kwargs['max_results'] = batch_size
        if start_index is not None:
            kwargs['first_result'] = start_index
        return self.app.apicall('entity.find', **kwargs)['results']

    def iterator(self, attributes=None, batch_size=None, filtering=None):
        """Iterate over records in the schema.
        Does not allow arbitrary sorting; sorts by id in order to use it
        for paging for efficiency reasons.

        Args:
            attributes: list of attributes to include
            batch_size: maximum results to return per batch
            filtering: filter to apply

        Yields:
            the next record
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
            records = self.find(
                attributes=attributes,
                sort_on=['id'],
                batch_size=batch_size,
                filtering=filtering,
            )
            if records:
                last_id = records[-1]['id']
                filtering = re.sub(r'id > (\d+)', 'id > {}'.format(last_id), filtering)
                for record in records:
                    if remove_id:
                        record.pop('id', None)
                    yield record
            else:
                break

    def csv_iterator(self, attributes, batch_size=None, filtering=None, headers=True):
        """Iterate over records in the schema and format as CSV.

        Newlines within fields will be escaped as '\\n' to ensure that each
        line contains an entire record.

        If a requested attribute is an object or plural it will be converted
        to a JSON string.

        Args:
            attributes: list of attributes to include
            batch_size: maximum results to return per batch
            filtering: filter to apply
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

        for record in self.iterator(**kwargs):
            row = [dot_lookup(record, attr) for attr in attributes]
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
