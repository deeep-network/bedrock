"""
netbox.py

A lookup function designed to return data from the NetBox instance
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
    author: Anthony Anderson (@anthonyra)
    name: netbox
    version_added: "1.0.0"
    short_description: Queries NetBox via its API
    description:
        - Queries NetBox via its API
    options:
        _terms:
            description:
                - The NetBox object type to query using Fully Qualified App Names
                - How tokens are set, you can not mix `netbox` and `plugins` _terms if they need different API tokens
            required: true
        _api:
            description:
                - The URL to the NetBox instance to query
            env:
                # in order of precendence
                - name: NETBOX_API
                - name: NETBOX_URL
            required: true
        filter:
            description:
                - The filter to use. Filters should be key value pairs separated by a space.
            required: false
        custom_headers:
            description:
                - To set a custom header on all requests. These headers are automatically merged with headers pynetbox sets itself.
            env:
                - name: NETBOX_CUSTOM_HEADERS
            required: false
        token:
            description:
                - The API token created through NetBox
                - This may not be required depending on the NetBox setup.
                - Can set `NETBOX_PLUGINS_TOKENS` for plugins if required (eg for netbox.secrets)
                - Can not mix `netbox` and `plugins` _terms if they require different API tokens
            env:
                # in order of precendence
                - name: NETBOX_TOKEN
                - name: NETBOX_PLUGINS_TOKEN
                - name: NETBOX_API_TOKEN
            required: false
        validate_certs:
            description:
                - Whether or not to validate SSL of the NetBox instance
            required: false
            default: true
    requirements:
        - pynetbox
        - requests
"""

EXAMPLES = """
tasks:
  # query a list of devices using ENV file
  - name: Obtain list of devices from NetBox
    ansible.builtin.debug:
      msg: >
        "Device {{ item.value.display_name }} (ID: {{ item.key }}) was
         manufactured by {{ item.value.device_type.manufacturer.name }}"
    loop: "{{ query('depin.libs.netbox', 'netbox.dcim.devices' }}"

    # This example uses an API Filter
  - name: Obtain list of devices from NetBox
    debug:
      msg: >
        "Device {{ item.value.display_name }} (ID: {{ item.key }}) was
         manufactured by {{ item.value.device_type.manufacturer.name }}"
    loop: "{{ query('depin.libs.netbox', 'dcim.devices', filter='role=management tag=Dell' }}"

  # query a secret from Netbox Secrets with all options set
  - name: Obtain Netbox secret
    debug:
      msg: >
        "Secret {{ item.value.plaintext }} (ID: {{ item.key }})"
    loop: "{{ query('depin.libs.netbox', 'plugins.secrets.secrets',
                    api='http://localhost/',
                    custom_headers='{
                        CF-Access-Client-Id: '<redacted>',
                        CF-Access-Client-Secret: '<redacted>'
                    }',
                    token='<redacted>'),
                    validate_certs=False,
                    session_key='<redacted>',
                    filter='assigned_object=<id>'
            }}"
"""

RETURN = """
  _list:
    description:
      - list of composed dictionaries with key and value
    type: list
"""

import os
import json
import functools
from pprint import pformat

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.parsing.splitter import parse_kv, split_args
from ansible.utils.display import Display
from ansible.module_utils.six import raise_from

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

def get_endpoint(netbox, fqan):
    """
    get_endpoint(netbox, name)
        netbox: a predefined pynetbox.api() pointing to a valid instance
                of NetBox
        fqan: the fully qualified app name (netbox.dcim.devices or dcim.devices) or 
             (plugins.secrets.secrets) passed to the lookup function
    """
    pynetbox_version = tuple(map(int, pynetbox.__version__.split(".")))
    _fqan = fqan.split('.')

    if _fqan[0] == 'plugins':
        return functools.reduce(getattr, _fqan, netbox)
    else:
        _fqan = [name.replace('-','_') for name in _fqan]
        if pynetbox_version < (6, 4) and "wireless" in fqan:
            Display().v(
                "pynetbox version %d does not support wireless app; please update to v6.4.0 or newer."
                % (".".join(pynetbox_version))
            )

        if pynetbox_version < (7, 0, 1) and "secret" in fqan:
            Display().v(
                "pynetbox version %d does not support secrets; please update to v7.0.1 or newer."
                % (".".join(pynetbox_version))
            )

        if pynetbox_version < (7, 3) and "l2vpn" in fqan:
            Display().v(
                "pynetbox version %d does not support vpn app; please update to v7.3.0 or newer."
                % (".".join(pynetbox_version))
            )

        if _fqan[0] == 'netbox':
            _fqan.pop(0)
        return functools.reduce(getattr, _fqan, netbox)

def build_filters(filters):
    """
    This will build the filters to be handed to NetBox endpoint call if they exist.

    Args:
        filters (str): String of filters to parse.

    Returns:
        result (list): List of dictionaries to filter by.
    """
    filter = {}
    args_split = split_args(filters)
    args = [parse_kv(x) for x in args_split]
    for arg in args:
        for k, v in arg.items():
            if k not in filter:
                filter[k] = list()
                filter[k].append(v)
            else:
                filter[k].append(v)
    return filter

def fetch(api_endpoint, filters=None):
    """
    Wrapper for calls to NetBox and handle any possible errors.

    Args:
        nb_endpoint (object): The NetBox endpoint object to make calls.

    Returns:
        results (object): Pynetbox result.

    Raises:
        AnsibleError: Ansible Error containing an error message.
    """
    try:
        if filters:
            results = api_endpoint.filter(**filters)
        else:
            results = api_endpoint.all()
    except pynetbox.RequestError as e:
        if e.req.status_code == 404 and "plugins" in e:
            raise AnsibleError(
                "{0} - Not a valid plugin endpoint, please make sure to provide valid plugin endpoint.".format(
                    e.error
                )
            )
        else:
            raise AnsibleError(e.error)

    return results


class LookupModule(LookupBase):
    """
    LookupModule(LookupBase) is defined by Ansible
    """

    def run(self, terms, variables=None, **kwargs):
        Display().vvvv(
            "NetBox lookup for %s with %s"
            % (terms, kwargs)
        )

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

        if not isinstance(terms, list):
            terms = [terms]

        netbox_api_token = (
            kwargs.get("token")
            or os.getenv("NETBOX_PLUGINS_TOKEN") if "plugins" in terms[0] else os.getenv("NETBOX_TOKEN")
            or os.getenv("NETBOX_API_TOKEN")
        )

        netbox_api_endpoint = (
            kwargs.get("api")
            or os.getenv("NETBOX_API")
            or os.getenv("NETBOX_URL")
        )

        netbox_custom_headers = (
            kwargs.get("custom_headers")
            or os.getenv("NETBOX_CUSTOM_HEADERS")
            or dict()
        )

        if isinstance(netbox_custom_headers, str):
            netbox_custom_headers = json.loads(netbox_custom_headers)

        netbox_ssl_verify = kwargs.get("validate_certs", True)

        netbox_filter = (
            kwargs.get("filter")
            or kwargs.get("filters")
        )
        ## short circuit if passed in False for filter
        if netbox_filter == False:
            return []

        try:
            netbox_secrets_session_key = variables['ansible_facts']['session_key']
        except (NameError, AttributeError, KeyError):
            netbox_secrets_session_key = (
                kwargs.get("session_key", None)
                or os.getenv("NETBOX_SECRETS_SESSION_KEY")
            )

        if netbox_secrets_session_key is not None:
            netbox_custom_headers['X-Session-Key'] = netbox_secrets_session_key

        session = requests.Session()
        session.verify = netbox_ssl_verify

        if netbox_custom_headers:
            Display().vvvv(
                "%s"
                % (netbox_custom_headers)
            )
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

        results = []
        for term in terms:
            try:
                endpoint = get_endpoint(netbox, term)
            except KeyError:
                raise AnsibleError(
                    "Unrecognised FQAN %s. Check documentation" % term
                )

            Display().vvvv(
                "NetBox lookup for %s to %s using token %s filter %s"
                % (term, netbox_api_endpoint, netbox_api_token, netbox_filter)
            )

            if netbox_filter:
                filter = build_filters(netbox_filter)
                
                id = filter.get('id', None)
                if id is None:
                    id = filter.get('_raw_params', None)

                if id:
                    if isinstance(id, list):
                        id = id[0]

                    Display().vvvv(
                        "ID set %s, will use .get instead of .filter"
                        % (id)
                    )
                    try:
                        nb_data = endpoint.get(int(id))
                        if nb_data is None:
                            return []
                        
                        data = dict(nb_data)
                        Display().vvvvv(pformat(data))
                        return [data]
                    except pynetbox.RequestError as e:
                        raise AnsibleError(e.error)

                Display().vvvv("filter is %s" % filter)

            # Make call to NetBox API and capture any failures
            nb_data = fetch(
                endpoint, filters=filter if netbox_filter else None
            )

            for data in nb_data:
                data = dict(data)
                Display().vvvvv(pformat(data))
                results.append(data)

        return results
