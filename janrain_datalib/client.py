"""Client class."""
from janrain_datalib.clientsettings import ClientSettings
from janrain_datalib.exceptions import NotFoundError

class Client(object):
    """Encapsulates a client."""

    def __init__(self, app, client_id):
        """Initialize.

        Args:
            app: App object
            client_id: client_id of client
        """
        self._app = app
        self._client_id = client_id
        self._settings = ClientSettings(app, client_id)

    @property
    def app(self):
        """:class:`.App` object."""
        return self._app

    @property
    def client_id(self):
        """Client client_id."""
        return self._client_id

    @property
    def settings(self):
        """:class:`.ClientSettings` object."""
        return self._settings

    def create(self, description, features=None):
        """Create a new client.

        Args:
            description: client description
            features: list of features

        Returns:
            new client_id
        """
        kwargs = {'description': description}
        if features:
            kwargs['features'] = features
        else:
            features = []
        r = self.app.apicall('clients/add', **kwargs)
        client_id = r['client_id']
        client_secret = r['client_secret']

        client_def = {
            'client_id': client_id,
            'client_secret': client_secret,
            'description': description,
            'features': features,
            'whitelist': ['0.0.0.0/0'],
        }

        # update cache
        cache_key = 'clients.{}'.format(client_id)
        self.app.set_cache(cache_key, client_def)

        self._client_id = client_id
        self._settings = ClientSettings(self.app, client_id)

        return client_id

    def delete(self):
        """Delete client."""
        kwargs = {
            'client_id_for_deletion': self.client_id,
        }
        self.app.apicall('clients/delete', **kwargs)

        # update cache
        cache_key = 'clients.{}'.format(self.client_id)
        self.app.del_cache(cache_key)

    def reset_secret(self, hours_to_live=None):
        """Give client a new client_secret.

        Args:
            hours_to_live: hours that the old secret will remain valid
                (default: api default)

        Returns:
            new client_secret
        """
        kwargs = {
            'for_client_id': self.client_id,
        }
        if hours_to_live:
            kwargs['hours_to_live'] = hours_to_live
        r = self.app.apicall('clients/reset_secret', **kwargs)
        client_secret = r['new_secret']

        # update cache
        cache_key = 'clients.{}.client_secret'.format(self.client_id)
        self.app.set_cache(cache_key, client_secret)

        return client_secret

    def as_dict(self):
        """The raw client definition.

        Returns:
            client definition

        Raises:
            NotFoundError: if client not found
        """
        try:
            return dict(self.app.clients_as_dict()[self.client_id])
        except KeyError:
            raise NotFoundError("client does not exist: {}".format(self.client_id))

    def set_description(self, description):
        """Set description.

        Args:
            description: client description
        """
        kwargs = {
            'for_client_id': self.client_id,
            'description': description,
        }
        self.app.apicall('clients/set_description', **kwargs)

        # update cache
        cache_key = 'clients.{}.description'.format(self.client_id)
        self.app.set_cache(cache_key, description)

    def set_features(self, features):
        """Set features.

        Args:
            features: list of client features
        """
        kwargs = {
            'for_client_id': self.client_id,
            'features': features,
        }
        self.app.apicall('clients/set_features', **kwargs)

        # update cache
        cache_key = 'clients.{}.features'.format(self.client_id)
        self.app.set_cache(cache_key, features)

    def set_whitelist(self, whitelist):
        """Set whitelist.

        Args:
            whitelist: list of IP blocks
        """
        kwargs = {
            'for_client_id': self.client_id,
            'whitelist': whitelist,
        }
        self.app.apicall('clients/set_whitelist', **kwargs)

        # update cache
        cache_key = 'clients.{}.whitelist'.format(self.client_id)
        self.app.set_cache(cache_key, whitelist)
