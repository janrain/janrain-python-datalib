"""App class."""
import logging

import requests.exceptions
import janrain.capture

from janrain_datalib.exceptions import ApiError
from janrain_datalib.exceptions import ApiAuthError
from janrain_datalib.exceptions import ApiInputError
from janrain_datalib.exceptions import ApiUpdateError
from janrain_datalib.exceptions import ApiNotFoundError
from janrain_datalib.exceptions import ApiTooLargeError
from janrain_datalib.exceptions import ApiRateLimitError
from janrain_datalib.defaultsettings import DefaultSettings
from janrain_datalib.client import Client
from janrain_datalib.schema import Schema

def get_app(application_url, client_id, client_secret, application_id=None):
    """Get an :class:`.App` object.

    Args:
        application_url: capture application url
        client_id: client_id with admin priveleges
        client_secret: client_secret for client_id
        application_id: application id

    Returns:
        an App object
    """
    defaults = {
        'client_id': client_id,
        'client_secret': client_secret,
    }
    if application_id is not None:
        defaults['application_id'] = application_id
    api = janrain.capture.Api(application_url, defaults)
    return App(api)

class App(object):
    """Encapsulates a Capture app."""

    def __init__(self, api):
        """Initialize app.

        Args:
            api: a janrain.capture.Api object
        """
        self.api = api
        self.default_settings = DefaultSettings(self)
        self.logger = logging.getLogger('janrain_datalib')
        self.logger.addHandler(logging.NullHandler())
        self._cache = {}

    def apicall(self, cmd, **kwargs):
        """Make an api call.

        Args:
            cmd: api endpoint (e.g. entityType.list)
            **kwargs: arbitrary keyword args for the api call

        Returns:
            response from the api

        Raises:
            ApiError: all kinds
        """
        try:
            self.logger.debug("apicall: %s", cmd)
            return self.api.call(cmd, **kwargs)

        except janrain.capture.ApiResponseError as err:
            err_msg = str(err)
            self.logger.error("api error: %s", cmd)
            if (err.code == 402
                    or err.code == 403
                    or err.code == 431
                    or "malformed" in err_msg
                    or "not a valid id" in err_msg):
                raise ApiAuthError(err_msg, err.code)
            if err.code == 404 or err.code == 222 or "not found" in err_msg:
                raise ApiNotFoundError(err_msg, err.code)
            if err.code == 226 and "changes have been made" in err_msg:
                raise ApiUpdateError(err_msg, err.code)
            if "for_client_id" in err_msg or "flow_body" in err_msg:
                raise ApiInputError(err_msg, err.code)
            raise ApiError(err_msg, err.code)

        except requests.exceptions.HTTPError as err:
            self.logger.error("http error: %s", cmd)
            if (err.response.status_code == 403
                    and "too large" in err.response.text
                    or err.response.status_code == 502
                    or err.response.status_code == 504):
                raise ApiTooLargeError("request was too large", err.response.status_code)
            if err.response.status_code == 510:
                raise ApiRateLimitError("rate limit exceeded", err.response.status_code)
            # something else happened
            raise

        except Exception:
            # most likely these will be other Requests errors
            self.logger.error("other error: %s", cmd)
            raise

    def get_cache(self, key=None):
        """Retrieve a value from the cache.
        If key is not specified, return entire cache.

        Args:
            key: dot-separated string

        Returns:
            value in the cache

        Raises:
            KeyError: if key is not in the cache
        """
        def dict_get(data, path):
            """Lookup a value from a dict."""
            try:
                if len(path) > 1:
                    return dict_get(data[path[0]], path[1:])
                else:
                    return data[path[0]]
            except TypeError:
                raise KeyError(path[0])

        if key:
            return dict_get(self._cache, key.split('.'))
        else:
            return self._cache

    def set_cache(self, key, value, force=False):
        """Set a value in the cache.

        Args:
            key: dot-separated string
            value: value to set
            force: whether to create missing parent keys,
                (default is to not set the value if parent keys are missing)
        """
        def dict_set(data, path, value, force=False):
            """Assign a value at a path in a dict."""
            try:
                if len(path) > 1:
                    if force:
                        data[path[0]] = {}
                    dict_set(data[path[0]], path[1:], value, force=force)
                else:
                    data[path[0]] = value
            except (KeyError, TypeError):
                pass

        dict_set(self._cache, key.split('.'), value, force=force)

    def del_cache(self, key=None):
        """Clear cached data.
        If key is not specified, entire cache is cleared.
        If key does not exist in the cache, nothing happens.

        Args:
            key: dot-separated string
        """
        def dict_delete(data, path):
            """Delete a value from a dict."""
            try:
                if len(path) > 1:
                    dict_delete(data[path[0]], path[1:])
                else:
                    del data[path[0]]
            except (KeyError, TypeError):
                pass  # invalid path - do nothing

        if key:
            dict_delete(self._cache, key.split('.'))
        else:
            # clear entire cache
            self._cache = {}

    def clients_as_dict(self):
        """All clients as a dict.

        Returns:
            dict of all clients
        """
        cache_key = 'clients'
        try:
            return self.get_cache(cache_key)
        except KeyError:
            pass

        r = self.apicall('clients/list')
        clients_list = r['results']
        clients = {x['client_id']: x for x in clients_list}
        # update cache
        self.set_cache(cache_key, clients)

        return clients

    def settings_as_dict(self):
        """All default and client settings as a dict.

        Returns:
            dict of all settings
        """
        cache_key = 'settings'
        try:
            return self.get_cache(cache_key)
        except KeyError:
            pass

        r = self.apicall('settings/get_all')
        settings = {
            'client_settings': r['client_settings'],
            'default_settings': r['default_settings'],
        }
        # update cache
        self.set_cache(cache_key, settings)

        return settings

    def list_schemas(self):
        """List the names of all schemas.

        Returns:
            list of schema names
        """
        cache_key = 'schema_names'
        try:
            return self.get_cache(cache_key)
        except (KeyError, AttributeError):
            r = self.apicall('entityType.list')
            names = r['results']
            # update cache
            self.set_cache(cache_key, names)

            return names

    def get_client(self, client_id=None):
        """Get a :class:`.Client` object.

        Args:
            client_id: client_id of client
                (can be omitted when creating a client)

        Returns:
            a Client object
        """
        return Client(self, client_id)

    def get_schema(self, schema_name):
        """Get a :class:`.Schema` object.

        Args:
            schema_name: name of schema

        Returns:
            a Schema object
        """
        return Schema(self, schema_name)
