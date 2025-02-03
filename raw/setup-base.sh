#!/bin/bash

# Check if running as the desired user
if [ "$(id -u -n)" != "nerdnode" ]; then
    # Re-run this script as nerdnode
    exec su nerdnode -c 'bash <(cat)'
fi

backoff=5  # Starting backoff time in seconds
max_backoff=$((5 * 60))  # 5 minutes in seconds
attempt=1

## install hab on local host to be able to install ansible
curl https://raw.githubusercontent.com/habitat-sh/habitat/main/components/hab/install.sh | sudo bash
sudo hab license accept
sudo hab origin key download deeep-network

while true; do
    echo "Attempt $attempt: Installing deeep-network/ansible..."
    if sudo hab pkg install deeep-network/ansible; then
        echo "Successfully installed ansible package"
        break
    fi

    echo "Retrying in $backoff seconds..."
    sleep $backoff

    backoff=$((backoff * 2 < max_backoff ? backoff * 2 : max_backoff))
    attempt=$((attempt + 1))
done

ansible-playbook deeep.core.setup
