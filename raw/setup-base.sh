#!/bin/bash

## install hab on local host
curl https://raw.githubusercontent.com/habitat-sh/habitat/main/components/hab/install.sh | sudo bash
sudo hab license accept
sudo hab origin key download deeep-network

## @todo - remove --channel unstable once fully migrated
until sudo hab pkg install deeep-network/ansible --channel unstable; do
    sleep 5
done

ansible-playbook deeep.core.setup
