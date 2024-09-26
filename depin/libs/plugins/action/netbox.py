#!/usr/bin/python
# Make coding more python3-ish, this is required for contributions to Ansible
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import re
import json
import functools
from pprint import pformat

from ansible.errors import AnsibleError
from ansible.module_utils.six import raise_from
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display

try:
    import pynetbox
except ImportError as imp_exc:
    PYNETBOX_LIBRARY_IMPORT_ERROR = imp_exc
else:
    PYNETBOX_LIBRARY_IMPORT_ERROR = None

try:
    import requests
except ImportError as imp_exc:
    REQUESTS_LIBRARY_IMPORT_ERROR = imp_exc
else:
    REQUESTS_LIBRARY_IMPORT_ERROR = None

# https://github.com/python/cpython/issues/74570#issuecomment-1093748531
os.environ['no_proxy']="*"

def safe_json(j):
    try:
        return json.loads(j)
    except json.JSONDecodeError as e:
        # Add quotes around values
        j = re.sub(r': *([^",\{\}\[\]]+)', r': "\1"', j)
        # Remove any double quotes that got added around existing quoted strings
        j = j.replace('""', '"')
    return json.loads(j)

def get_endpoint(netbox, app):
    """
    get_endpoint(netbox, name)
        netbox: a predefined pynetbox.api() pointing to a valid instance
                of NetBox
        app: the fully qualified app name (netbox.dcim.devices or dcim.devices) or 
             (plugins.secrets.secrets) passed to the lookup function
    """
    pynetbox_version = tuple(map(int, pynetbox.__version__.split(".")))
    _app = app.split('.')

    if _app[0] == 'plugins':
        return functools.reduce(getattr, _app, netbox)
    else:
        _app = [name.replace('-','_') for name in _app]
        if pynetbox_version < (6, 4) and "wireless" in app:
            Display().v(
                "pynetbox version %d does not support wireless app; please update to v6.4.0 or newer."
                % (".".join(pynetbox_version))
            )

        if pynetbox_version < (7, 0, 1) and "secret" in app:
            Display().v(
                "pynetbox version %d does not support secrets; please update to v7.0.1 or newer."
                % (".".join(pynetbox_version))
            )

        if pynetbox_version < (7, 3) and "l2vpn" in app:
            Display().v(
                "pynetbox version %d does not support vpn app; please update to v7.3.0 or newer."
                % (".".join(pynetbox_version))
            )

        if _app[0] == 'netbox':
            _app.pop(0)
        return functools.reduce(getattr, _app, netbox)

def format_fields(input):
    result = input
    if isinstance(result, str):
        result = json.loads(result)
    if 'id' in result and isinstance(result['id'], str):
        result['id'] = int(result['id'])
    if not isinstance(result, list):
        result = [result]
    return result

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp # tmp no longer has any effect

        if PYNETBOX_LIBRARY_IMPORT_ERROR:
            raise_from(
                AnsibleError("pynetbox must be installed to use this plugin"),
                PYNETBOX_LIBRARY_IMPORT_ERROR,
            )

        if REQUESTS_LIBRARY_IMPORT_ERROR:
            raise_from(
                AnsibleError("requests must be installed to use this plugin"),
                REQUESTS_LIBRARY_IMPORT_ERROR,
            )

        netbox_api_endpoint = (
            self._task.args.get('api')
            or os.getenv("NETBOX_API")
            or os.getenv("NETBOX_URL")
        )

        netbox_api_token = (
            self._task.args.get('token')
            or os.getenv("NETBOX_TOKEN")
            or os.getenv("NETBOX_API_TOKEN")
            or os.getenv("NETBOX_PLUGINS_TOKEN")
        )

        netbox_ssl_verify = (
            self._task.args.get('validate_certs')
            or os.getenv("NETBOX_VALIDATE_CERTS")
            or True
        )

        netbox_custom_headers = (
            self._task.args.get('custom_headers')
            or os.getenv("NETBOX_CUSTOM_HEADERS")
        )

        if isinstance(netbox_custom_headers, str):
            netbox_custom_headers = safe_json(netbox_custom_headers)

        netbox_app_name = (
            self._task.args.get('app')
            or os.getenv("NETBOX_APP")
        )

        netbox_create = (
            self._task.args.get('create')
            or None
        )

        netbox_update = (
            self._task.args.get('update')
            or None
        )

        netbox_delete = (
            self._task.args.get('delete')
            or None
        )

        if isinstance(netbox_custom_headers, str):
            netbox_custom_headers = safe_json(netbox_custom_headers)

        netbox_secrets_session_key = (
            self._task.args.get("session_key", None)
            or os.getenv("NETBOX_SECRETS_SESSION_KEY")
        )

        netbox_set_session_key = self._task.args.get("set_session_key", False)

        netbox_secrets_preserve_key = (
            self._task.args.get('perserve_key')
            or os.getenv("NETBOX_SECRETS_PERSERVE_KEY")
            or True
        )
            
        netbox_secrets_userkey = (
            self._task.args.get('userkey')
            or os.getenv("NETBOX_SECRETS_USERKEY")
        )

        if isinstance(netbox_secrets_userkey, str):
            netbox_secrets_userkey = safe_json(netbox_secrets_userkey)

        session = requests.Session()
        session.verify = netbox_ssl_verify

        try:
            netbox = pynetbox.api(
                netbox_api_endpoint,
                token=netbox_api_token if netbox_api_token else None
            )
        except TypeError:
            raise AnsibleError(
                "Error connecting to API check if missing token or required headers"
            )

        if netbox_custom_headers:
            session.headers = netbox_custom_headers
        netbox.http_session = session

        # if app name contains secrets and no session key provided attempt
        # to fetch one
        if netbox_set_session_key or (netbox_secrets_session_key is None and 'secrets' in netbox_app_name):
            session_key = netbox.plugins.secrets.session_keys.create(preserve_key=netbox_secrets_preserve_key, private_key=netbox_secrets_userkey['private_key'])
            netbox_secrets_session_key = session_key['session_key']

        # if session key was provided or fetched update the session headers
        if not netbox_secrets_session_key is None:
            result['ansible_facts'] = {'netbox_session_key': netbox_secrets_session_key}
            try:
                netbox_custom_headers['X-Session-Key'] = netbox_secrets_session_key
                session.headers = netbox_custom_headers
            except:
                raise AnsibleError(
                    "Failed retrieving session key for secrets"
                )

        if not netbox_app_name is None:
            try:
                endpoint = get_endpoint(netbox, netbox_app_name)
            except KeyError:
                raise AnsibleError(
                    "Unrecognised FQAN %s. Check documentation" % netbox_app_name
                )

            Display().vvvv(
                "NetBox action for %s to %s using token %s"
                % (netbox_app_name, netbox_api_endpoint, netbox_api_token)
            )

        result = { 'created': [], 'updated': [], 'deleted': [] }
        try:
            if not netbox_create is None:
                create = endpoint.create(format_fields(netbox_create))
                for record in create:
                    data = dict(record)
                    result['created'].append(data)
            if not netbox_update is None:
                update = endpoint.update(format_fields(netbox_update))
                for record in update:
                    data = dict(record)
                    result['updated'].append(data)
            if not netbox_delete is None:
                delete = endpoint.delete(format_fields(netbox_delete))
                for record in delete:
                    data = dict(record)
                    result['deleted'].append(data)
        except Exception as err:
             # @todo - figure out applicable error codes to catch here
             # and raise to Ansible
             Display().vvvv("%s" % (err))

        return result
