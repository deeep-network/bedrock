#!/bin/bash

if ! hab svc status | grep -q "ilert-heartbeat"; then
  echo "Loading ilert-heartbeat service..."
  hab svc load deeep-network/ilert-heartbeat
fi

hab pkg install deeep-network/ansible
## @todo - activate once we have an overlay network established
# if ! hab svc status | grep -q "manager"; then
#   echo "Loading DeEEP Manager service..."
#   hab svc load deeep-network/manager

#   # wait for receptor control socket
#   until [ -S /tmp/receptor.sock ]; do
#     echo "Waiting for receptor socket..."
#     sleep 2
#   done
# fi
