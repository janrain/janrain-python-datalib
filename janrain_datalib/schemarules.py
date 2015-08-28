"""SchemaRules class."""
from janrain_datalib.exceptions import NotFoundError

class SchemaRules(list):
    """Encapsulates a schema rules list."""

    def find(self, uuid):
        """Find a rule given its uuid.

        Args:
            path: attribute path/name

        Returns:
            rule definition

        Raises:
            NotFoundError: if rule is not found
        """
        for rule in self:
            if rule['uuid'] == uuid:
                return rule
        raise NotFoundError("rule not found")
