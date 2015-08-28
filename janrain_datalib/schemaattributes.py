"""SchemaAttributes class."""
from janrain_datalib.exceptions import NotFoundError

class SchemaAttributes(list):
    """Encapsulates a schema attributes list."""

    def find(self, path):
        """Find an attribute given its name or path.

        Args:
            path: attribute path/name

        Returns:
            attribute definition

        Raises:
            NotFoundError: if attribute is not found
        """
        # convert path to a list if not already
        if not isinstance(path, list):
            # split into a list
            path = path.strip('/').strip('.')
            path = path.replace('/', '.')
            path = path.split('.')

        for attr in self:
            # found a match
            if path[0] == attr['name']:
                # not done yet
                if len(path) > 1:
                    # recurse into sub attributes
                    if 'attr_defs' in attr:
                        attr_defs = self.__class__(attr['attr_defs'])
                        return attr_defs.find(path[1:])
                # found it
                else:
                    return attr

        raise NotFoundError("attribute not found")
