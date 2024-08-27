#!/usr/bin/python
# Make coding more python3-ish, this is required for contributions to Ansible
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json

from ansible.errors import AnsibleError
from ansible.module_utils.six import raise_from
from ansible.plugins.action import ActionBase

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
            or os.getenv("NETBOX_PLUGINS_TOKEN")
            or os.getenv("NETBOX_TOKEN")
            or os.getenv("NETBOX_API_TOKEN")
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
            netbox_custom_headers = json.loads(netbox_custom_headers)

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
            netbox_secrets_userkey = json.loads(netbox_secrets_userkey)
        
        session = requests.Session()
        session.verify = netbox_ssl_verify

        if netbox_custom_headers:
            session.headers = netbox_custom_headers

        try:
            netbox = pynetbox.api(
                netbox_api_endpoint,
                token=netbox_api_token if netbox_api_token else None
            )
        except TypeError:
            raise AnsibleError(
                "Error connecting to API check if missing token or required headers"
            )
        
        netbox.http_session = session
        session_key = netbox.plugins.secrets.session_keys.create(preserve_key=netbox_secrets_preserve_key, private_key=netbox_secrets_userkey['private_key'])

        try:
            _key = session_key['session_key']
            result['ansible_facts'] = {'session_key': _key}
        except KeyError:
            raise AnsibleError(
                "Unable to get Netbox secrets session key"
            )
        return result