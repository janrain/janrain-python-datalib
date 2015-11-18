"""Stand-alone utility functions and classes."""
import csv
import io
import json

def to_json(item, compact=False):
    """Convert item to JSON string.

    Example:
    >>> to_json({'a':'b'})
    '{\\n    "a": "b"\\n}'

    Args:
        item: thing to convert to JSON string
        compact: whether to compact the string

    Returns:
        JSON string
    """
    kwargs = {
        'ensure_ascii': False,
        'sort_keys': True,
    }
    if compact:
        kwargs['separators'] = (',', ':')
    else:
        kwargs['indent'] = 4
        kwargs['separators'] = (',', ': ')
    return json.dumps(item, **kwargs)

def to_csv(row):
    """Convert a list of items to a CSV string.

    Example:
    >>> to_csv(['first', '2nd,with,commas', 'lasty'])
    'first,"2nd,with,commas",lasty\\r\\n'

    Args:
        row: list of items to be formatted as CSV

    Returns:
        CSV record string
    """
    new_row = []
    for item in row:
        if item is None:
            # None/null should just be an empty string
            item = ''
        elif isinstance(item, str):
            # escape newlines
            item = item.replace('\n', '\\n')
        else:
            # convert to JSON string
            item = to_json(item, compact=True)
        new_row.append(item)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(new_row)
    return output.getvalue()

def dot_lookup(obj, path):
    """Lookup a value from a multi-level dict given a dot-separated path string.

    Example:
    >>> dot_lookup({'a':{'b':{'c':'test'}}}, 'a.b.c')
    'test'

    Args:
        obj: dict to look in
        path: dot-separated string

    Returns:
        item at path
    """
    for key in path.split('.'):
        obj = obj[key]
    return obj

def dot_assign(obj, path, value):
    """Assign a value to a multi-level dict.

    Example:
    >>> dot_assign({}, 'a.b.c', 'test')
    {'a': {'b': {'c': 'test'}}}

    Args:
        obj: dict to update
        path: dot-separated string
        value: value to assign

    Returns:
        updated obj
    """
    if isinstance(path, str):
        path = path.split('.')
    if len(path):
        key = path[0]
        if len(path) > 1:
            if key not in obj:
                obj[key] = {}
            sub_obj = obj[key]
            obj[key] = dot_assign(sub_obj, path[1:], value)
        else:
            obj[key] = value
    return obj

def to_capture_record(record, key_map=None, transform_map=None):
    """Returns a multilevel dict given a flat record.
    If key is missing from key_map, use original key.
    If transform function is missing from transform_map, do nothing.

    Example:
    >>> record = {'balance': '12.3'}
    >>> key_map = {'balance': 'wallet.balance'}
    >>> transform_map = {'balance': lambda x: float(x)}
    >>> to_capture_record(record, key_map, transform_map)
    {'wallet': {'balance': 12.3}}

    Args:
        record: single-level dict
        key_map: map of key in flat record to capture dot-path
        transform_map: map for key in flat record to a transform function;
            the transform function must take a single argument and return a
            single value

    Returns:
        multi-level dict
    """
    if key_map is None:
        key_map = {}
    if transform_map is None:
        transform_map = {}
    obj = {}
    for key in record:
        value = record[key]
        transform_func = transform_map.get(key, None)
        if transform_func:
            value = transform_func(value)
        path = key_map.get(key, key)
        dot_assign(obj, path, value)
    return obj
