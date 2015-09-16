"""Stand-alone utility functions and classes."""
import csv
import io
import json

def to_json(item, compact=False):
    """Convert item to JSON string.

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

def dot_lookup(data, path):
    """Lookup a value from a multilevel dict given a dot-separated path string.

    Args:
        data: dict
        path: dot-separated string

    Returns:
        item at path
    """
    for key in path.split('.'):
        data = data[key]
    return data
