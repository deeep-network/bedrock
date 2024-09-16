DOCUMENTATION = """
  author: Anthony Anderson (@anthonyra)
  name: netbox
  version_added: "1.0.0"
  short_description: Acquires a Netbox secrets session key
  description:
    - Acquires a Netbox secrets session key
  options:
    _api:
      description:
        - The URL to the NetBox instance to query
      env:
        # in order of precendence
        - name: NETBOX_API
        - name: NETBOX_URL
      required: true
    _userkey:
      descriptions:
        - The private key associated to a Netbox user with the correct permissions for Netbox secrets
      required: true
    custom_headers:
      description:
        - Used to set a custom header on all requests. These headers are automatically merged with headers pynetbox sets itself.
      env:
        - name: NETBOX_CUSTOM_HEADERS
      required: false
    perserve_key:
      descriptions:
        - Determines if the session key is ephemeral or not, when set to true the session key is saved to the database
      required: false
      default: true
    token:
      description:
        - The API token created through NetBox
        - Can set `NETBOX_PLUGINS_TOKENS` for plugins if required (eg for netbox.secrets)
        - Can not mix `netbox` and `plugins` _terms if they require different API tokens
        - This may not be required depending on the NetBox setup.
      env:
        # in order of precendence
        - name: NETBOX_PLUGINS_TOKEN
        - name: NETBOX_TOKEN
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
  # with only defaults set using ENV file
  - name: Get Netbox session key
    depin.libs.netbox_secrets_session:
"""

RETURN = """
  ansible_facts:
    description:
      - contains the `session_key` key/value pair
    type: dict
  changed:
    description:
      - basic Ansible response
    type: bool
  failed:
    description:
      - basic Ansible response
    type: bool
"""