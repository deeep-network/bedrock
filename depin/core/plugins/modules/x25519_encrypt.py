#!/usr/bin/python

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: x25519_encrypt
short_description: Encrypt data using X25519 public key encryption
description:
    - This module encrypts data using X25519 public key encryption
    - Can generate new keypairs or use existing ones
    - Supports both encryption and decryption operations
    - Supports loading keys from environment variables
options:
    state:
        description:
            - The operation to perform
        choices: ['encrypt', 'decrypt', 'generate_keypair']
        required: true
        type: str
    data:
        description:
            - The data to encrypt or decrypt
        type: str
        required: false
    public_key:
        description:
            - The recipient's public key in raw, file or base64 format
            - Can also be set via X25519_PUBLIC_KEY environment variable
        type: str
        required: false
    private_key:
        description:
            - The recipient's private key in raw, file or base64 format
            - Can also be set via X25519_PRIVATE_KEY environment variable
            - Only needed for decryption
        type: str
        required: false
    path:
        description:
            - Optional path to save generated keys
        type: str
        required: false
requirements:
    - pynacl
author:
    - Anthony Anderson <anthony@deeep.network>
"""

EXAMPLES = r"""
# Generate a new keypair
- name: Generate X25519 keypair
  depin.core.x25519_encrypt:
    state: generate_keypair
    path: /path/to/save/keys
  register: keypair

# Encrypt data using public key from environment variable
- name: Encrypt sensitive data
  depin.core.x25519_encrypt:
    state: encrypt
    data: "Secret message"
  environment:
    X25519_PUBLIC_KEY: "{{ recipient_public_key }}"
  register: encrypted_data

# Decrypt data using private key from environment variable
- name: Decrypt data
  depin.core.x25519_encrypt:
    state: decrypt
    data: "{{ encrypted_data }}"
  environment:
    X25519_PRIVATE_KEY: "{{ private_key }}"
  register: decrypted_data
"""

RETURN = r"""
public_key:
    description: Base64 encoded public key (when generating keypair)
    type: str
    returned: when state=generate_keypair
private_key:
    description: Base64 encoded private key (when generating keypair)
    type: str
    returned: when state=generate_keypair
encrypted_data:
    description: Base64 encoded encrypted data
    type: str
    returned: when state=encrypt
decrypted_data:
    description: Decrypted data
    type: str
    returned: when state=decrypt
"""

import base64
import os
from ansible.module_utils.basic import AnsibleModule
try:
    from nacl.public import PrivateKey, PublicKey, SealedBox
    HAS_NACL = True
except ImportError:
    HAS_NACL = False

def generate_keypair():
    """Generate a new X25519 keypair"""
    private_key = PrivateKey.generate()
    public_key = private_key.public_key
    
    private_key_b64 = base64.b64encode(bytes(private_key)).decode('utf-8')
    public_key_b64 = base64.b64encode(bytes(public_key)).decode('utf-8')
    return private_key_b64, public_key_b64

def _get_key_from_env_or_param(param_value, env_var_name):
    """Get key from environment variable or parameter"""
    if os.environ.get(env_var_name):
        return os.environ[env_var_name]
    return param_value

def _get_key(key_data, key_type):
    """
    Process key from file, base64, or raw format
    
    Args:
        key_data: The key data to process
        key_type: Either PublicKey or PrivateKey class from nacl.public
        
    Returns:
        Processed public or private key object
    """
    _key_type = 'public' if key_type == PublicKey else 'private'
    if not key_data:
        raise ValueError(f"No {_key_type} key provided")
        
    if os.path.isfile(key_data):
        with open(key_data, 'rb') as f:
            key_data = f.read().strip()

    try:
        return key_type(key_data)
    except:
        try:
            return key_type(base64.b64decode(key_data))
        except:
            try:
                return key_type(key_data.encode('utf-8'))
            except Exception as e:
                raise ValueError(f"Unable to process {_key_type} key: {str(e)}")


def encrypt_message(message, recipient_public_key_input):
    """
    Encrypt a message using either a public key or by deriving it from a private key

    Args:
        message: Message to encrypt
        recipient_public_key_input: Either a public key (base64/raw/file) or
        private key (base64/raw/file) to derive public key from

    Returns:
        Base64 encoded encrypted message
    """
    try:
        # Get public key from environment or parameter
        key_data = _get_key_from_env_or_param(
            recipient_public_key_input,
            'X25519_PUBLIC_KEY'
        )

        public_key = _get_key(key_data, PublicKey)
        sealed_box = SealedBox(public_key)
        encrypted = sealed_box.encrypt(message.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')
    except Exception as e:
        raise ValueError(f"Unable to encrypt message: {str(e)}")

def decrypt_message(encrypted_message_b64, private_key_input):
    """
    Decrypt a message using the recipient's private key

    Args:
        encrypted_message_b64: Base64 encoded encrypted message
        private_key_input: A private key (base64/raw/file)

    Returns:
        Decrypted message string
    """
    # Get private key from environment or parameter
    key_data = _get_key_from_env_or_param(
        private_key_input,
        'X25519_PRIVATE_KEY'
    )

    private_key = _get_key(key_data, PrivateKey)
    sealed_box = SealedBox(private_key)
    encrypted = base64.b64decode(encrypted_message_b64)
    decrypted = sealed_box.decrypt(encrypted)
    return decrypted.decode('utf-8')

def main():
    module_args = dict(
        state=dict(type='str', required=True, choices=['encrypt', 'decrypt', 'generate_keypair']),
        data=dict(type='str', required=False, no_log=True),
        public_key=dict(type='str', required=False),
        private_key=dict(type='str', required=False, no_log=True),
        path=dict(type='str', required=False)
    )

    result = dict(
        changed=False,
        public_key=None,
        private_key=None,
        encrypted_data=None,
        decrypted_data=None
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if not HAS_NACL:
        module.fail_json(msg='PyNaCl library is required for this module')

    if module.check_mode:
        module.exit_json(**result)

    state = module.params['state']

    try:
        if state == 'generate_keypair':
            private_key, public_key = generate_keypair()
            result['private_key'] = private_key
            result['public_key'] = public_key
            result['changed'] = True

            if module.params['path']:
                path = module.params['path']
                with open(os.path.join(path, 'public_key.b64'), 'w') as f:
                    f.write(public_key)
                with open(os.path.join(path, 'private_key.b64'), 'w') as f:
                    f.write(private_key)

        elif state == 'encrypt':
            if not module.params['data']:
                module.fail_json(msg='data is required for encryption')

            encrypted = encrypt_message(
                module.params['data'],
                module.params['public_key']
            )
            result['encrypted_data'] = encrypted
            result['changed'] = True

        elif state == 'decrypt':
            if not module.params['data']:
                module.fail_json(msg='data is required for decryption')

            decrypted = decrypt_message(
                module.params['data'],
                module.params['private_key']
            )
            result['decrypted_data'] = decrypted
            result['changed'] = True

    except Exception as e:
        module.fail_json(msg=f'Error: {str(e)}')

    module.exit_json(**result)

if __name__ == '__main__':
    main()
