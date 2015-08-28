"""DefaultSettings class."""

class DefaultSettings(object):
    """Encapsulates application default settings."""

    def __init__(self, app):
        """Initialize.

        Args:
            app: App object
        """
        self._app = app

    @property
    def app(self):
        """:class:`.App` object."""
        return self._app

    def get(self, key):
        """Get a default setting.
        If it does not exist, return None

        Args:
            key: setting key

        Returns:
            setting value
        """
        all_settings = self.app.settings_as_dict()
        try:
            return all_settings['default_settings'][key]
        except KeyError:
            return None

    def get_all(self):
        """Get all default settings.

        Returns:
            map of keys to values
        """
        all_settings = self.app.settings_as_dict()
        return all_settings['default_settings']

    def set(self, key, value):
        """Set a default setting.

        Args:
            key: setting key
            value: setting value

        Returns:
            True if updated, False if created
        """
        kwargs = {
            'key': key,
            'value': value,
        }
        r = self.app.apicall('settings/set_default', **kwargs)
        updated = r['result']

        # update cache
        cache_key = 'settings.default_settings.{}'.format(key)
        self.app.set_cache(cache_key, value)

        return updated

    def set_multi(self, items):
        """Set multiple default settings.

        Args:
            items: map of keys to values

        Returns:
            map of keys to results (True if updated, False if created)
        """
        kwargs = {
            'items': items,
        }
        r = self.app.apicall('settings/set_default_multi', **kwargs)
        report = r['result']

        # update cache
        for key in items:
            cache_key = 'settings.default_settings.{}'.format(key)
            self.app.set_cache(cache_key, items[key])

        return report

    def delete(self, key):
        """Delete a default setting.

        Args:
            key: setting key

        Returns:
            True if setting existed, False if not
        """
        kwargs = {
            'key': key,
        }
        r = self.app.apicall('settings/delete_default', **kwargs)
        existed = r['result']

        # update cache
        cache_key = 'settings.default_settings.{}'.format(key)
        self.app.del_cache(cache_key)

        return existed
