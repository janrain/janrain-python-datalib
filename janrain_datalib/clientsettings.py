"""ClientSettings class."""

class ClientSettings(object):
    """Encapsulates client settings."""

    def __init__(self, app, client_id):
        """Initialize.

        Args:
            app: App object
            client_id: client_id of client
        """
        self._app = app
        self._client_id = client_id

    @property
    def app(self):
        """:class:`.App` object."""
        return self._app

    @property
    def client_id(self):
        """Client's client_id."""
        return self._client_id

    def get(self, key):
        """Get a setting.
        If client setting is not found, return default setting.
        If default setting is not found, return None.

        Args:
            key: setting key

        Returns:
            setting value
        """
        all_settings = self.app.settings_as_dict()
        try:
            return all_settings['client_settings'][self.client_id][key]
        except KeyError:
            try:
                return all_settings['default_settings'][key]
            except KeyError:
                return None

    def get_all(self):
        """Get all settings for the client.
        Includes default settings unless overridden by client settings.

        Returns:
            map of keys to values
        """
        all_settings = self.app.settings_as_dict()
        settings = all_settings['default_settings']
        client_settings = all_settings['client_settings'].get(self.client_id, {})
        settings.update(client_settings)

        return settings

    def set(self, key, value):
        """Set a client setting.

        Args:
            key: setting key
            value: setting value

        Returns:
            True if updated, False if created
        """
        kwargs = {
            'key': key,
            'value': value,
            'for_client_id': self.client_id,
        }
        r = self.app.apicall('settings/set', **kwargs)
        updated = r['result']

        # update cache
        cache_key = 'settings.client_settings.{}.{}'.format(self.client_id, key)
        self.app.set_cache(cache_key, value)

        return updated

    def set_multi(self, items):
        """Set multiple client settings.

        Args:
            items: map of keys to values

        Returns:
            map of keys to results (True if updated, False if created)
        """
        kwargs = {
            'items': items,
            'for_client_id': self.client_id,
        }
        r = self.app.apicall('settings/set_multi', **kwargs)
        report = r['result']

        # update cache
        for key in items:
            cache_key = 'settings.client_settings.{}.{}'.format(self.client_id, key)
            self.app.set_cache(cache_key, items[key])

        return report

    def delete(self, key):
        """Delete a client setting.

        Args:
            key: setting key

        Returns:
            True if setting existed, False if not
        """
        kwargs = {
            'for_client_id': self.client_id,
            'key': key,
        }
        r = self.app.apicall('settings/delete', **kwargs)
        existed = r['result']

        # update cache
        cache_key = 'settings.client_settings.{}.{}'.format(self.client_id, key)
        self.app.del_cache(cache_key)

        return existed
