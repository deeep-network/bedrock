#!/bin/bash

## install hab on local host
curl https://raw.githubusercontent.com/habitat-sh/habitat/main/components/hab/install.sh | bash
sudo hab license accept
sudo hab origin key download deeep-network

until sudo hab pkg install deeep-network/ansible; do
    sleep 5
done

source /etc/profile
until ansible-playbook deeep.core.setup; do
    sleep 5
done
