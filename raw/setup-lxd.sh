#!/bin/bash

declare -a instances_to_create=()

# Check if HAB_AUTH_TOKEN is set
source /etc/environment
if [ -z "${HAB_AUTH_TOKEN}" ]; then
    echo "Error: HAB_AUTH_TOKEN environment variable must be set"
    exit 1
fi

# Setup LXD
lxd activateifneeded
lxd_preseed=$(cat << 'EOF'
config:
  images.auto_update_interval: "0"
networks:
  - config:
      ipv4.address: auto
      ipv6.address: auto
    description: ""
    name: lxdbr0
    type: bridge
    project: default
storage_pools:
  - name: default
    driver: zfs
    config:
      source: default/lxd
profiles:
  - config: {}
    description: "Default LXD profile"
    devices:
      eth0:
        name: eth0
        network: lxdbr0
        type: nic
      root:
        path: /
        pool: default
        type: disk
    name: default
projects: []
cluster: null
EOF
)

echo "$lxd_preseed" | lxd init --preseed || {
    echo "Error applying preseed configuration"
    exit 1
}

lxd waitready --timeout 300 || {
    echo "Error waiting for LXD"
    exit 1
}

# Create cloud-init for VM
create_cloud_init() {
local name=$1
local supervisor_config=$2

local cloud_config=$(cat << EOF
#cloud-config

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
      HAB_AUTH_TOKEN=${HAB_AUTH_TOKEN}
      PULUMI_ACCESS_TOKEN=${PULUMI_ACCESS_TOKEN}

  - path: /etc/systemd/system/hab-supervisor.service
    content: |
      [Unit]
      Description=The Chef Habitat Supervisor

      [Service]
      EnvironmentFile=/etc/environment
      Restart=always
      ExecStart=/usr/bin/hab sup run ${supervisor_config}

      [Install]
      WantedBy=default.target

runcmd:
  - curl https://raw.githubusercontent.com/habitat-sh/habitat/main/components/hab/install.sh | bash
  - hab license accept
  - hab origin key download deeep-network
  - systemctl daemon-reload
  - systemctl enable hab-supervisor.service
  - systemctl start hab-supervisor.service
EOF
)

    lxc profile delete "$name" >/dev/null 2>&1 || true
    lxc profile copy default "$name"
    lxc profile set "$name" cloud-init.user-data="$cloud_config"
    instances_to_create+=("$name")
}

# Create bastion profiles
for i in {1..3}; do
    peer1=$(( (i % 3) + 1 ))
    peer2=$(( ((i + 1) % 3) + 1 ))
    create_cloud_init "hab-bastion-${i}" "\\
        --permanent-peer \\
        --peer=hab-bastion-${peer1}.lxd \\
        --peer=hab-bastion-${peer2}.lxd"
done

# Create vmagent profile
create_cloud_init "vmagent" "deeep-network/vmagent \\
        --keep-latest-packages 2 \\
        --strategy at-once"

# Wait for profiles to settle
sleep 5

# Launch all instances
for instance in "${instances_to_create[@]}"; do
    echo "Launching $instance..."
    lxc launch "ubuntu:24.04" "$instance" --vm --profile "$instance" --quiet
    sleep 5
done
