#!/bin/bash

# Check if HAB_AUTH_TOKEN is set
source /etc/environment
if [ -z "${HAB_AUTH_TOKEN}" ]; then
    echo "Error: HAB_AUTH_TOKEN environment variable must be set"
    exit 1
fi

## Setup LXD
lxd_preseed='config: {}
networks:
  - name: lxdbr0
    type: bridge
    description: ""
    project: default
    config:
      ipv4.address: auto
      ipv6.address: auto
storage_pools:
  - name: default
    driver: zfs
    config:
      source: default/lxd
profiles:
  - name: default
    description: Default LXD profile
    config: {}
    devices:
      eth0:
        name: eth0
        network: lxdbr0
        type: nic
      root:
        path: /
        pool: default
        type: disk
projects: []
cluster: null'

echo "$lxd_preseed" | sudo lxd init --preseed
sudo lxd activateifneeded
sudo lxd waitready --timeout 300

## Create Chef Habitat Bastion Ring
base_config="#cloud-config

packages:
  - curl
package_upgrade: true
package_update: true

users:
  - name: nerdnode
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /bin/bash

write_files:
  - path: /etc/environment
    append: true
    content: |
      HAB_AUTH_TOKEN=$HAB_AUTH_TOKEN
      PULUMI_ACCESS_TOKEN=$PULUMI_ACCESS_TOKEN"

for i in {1..3}; do
    # Calculate next two peers in cycle
    peer1=$(( (i % 3) + 1 ))
    peer2=$(( ((i + 1) % 3) + 1 ))

    config="$base_config
  - path: /etc/systemd/system/hab-supervisor.service
    content: |
      [Unit]
      Description=The Chef Habitat Supervisor

      [Service]
      EnvironmentFile=/etc/environment
      ExecStart=/usr/bin/hab sup run \\
        --permanent-peer \\
        --peer=hab-bastion-${peer1}.lxd \\
        --peer=hab-bastion-${peer2}.lxd

      [Install]
      WantedBy=default.target

runcmd:
  - curl https://raw.githubusercontent.com/habitat-sh/habitat/main/components/hab/install.sh | bash
  - hab license accept
  - systemctl daemon-reload
  - systemctl enable hab-supervisor.service
  - systemctl start hab-supervisor.service"

    echo "Setting up Chef Habitat Bastion Ring..."
    sudo lxc launch ubuntu:22.04 hab-bastion-${i} --config=cloud-init.user-data="$config"
done

## setup vmagent for metrics on hab-bastion-1
sudo lxc exec hab-bastion-1 -- sudo hab pkg install deeep-network/vmagent

## final setup enabling auto-deploy
curl https://raw.githubusercontent.com/deeep-network/bedrock/main/raw/setup-base.sh | bash
