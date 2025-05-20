#!/bin/bash

# Setup LXD
lxd activateifneeded

if lxc profile show default 2>/dev/null | grep -q "^devices: *{}$"; then
cat <<EOF | lxd init --preseed
  config: {}
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
fi

lxd waitready --timeout 300 || {
    echo "Error waiting for LXD"
    exit 1
}
