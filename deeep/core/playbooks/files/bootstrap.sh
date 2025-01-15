#!/bin/bash

if ! hab svc status | grep -q "ilert-heartbeat"; then
  echo "Loading ilert-heartbeat service..."
  hab svc load deeep-network/ilert-heartbeat
fi

if ! hab svc status | grep -q "ansible"; then
  echo "Installing step package..."
  hab pkg install deeep-network/step

  echo "Loading ansible service..."
  hab svc load deeep-network/ansible
fi
