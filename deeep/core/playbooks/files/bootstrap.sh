#!/bin/bash

if ! hab svc status | grep -q "ilert-heartbeat"; then
  echo "Loading ilert-heartbeat service..."
  hab svc load deeep-network/ilert-heartbeat
fi

if ! hab svc status | grep -q "ansible"; then
  echo "Installing step-cli package..."
  hab pkg install deeep-network/step

  echo "Loading ansible service..."
  hab svc load deeep-network/ansible

  # it takes a while for ansible-rulebook to spin up so lets
  # wait for it before calling the endpoint
  until curl -s http://127.0.0.1:33337 >/dev/null 2>&1; do
    echo "Waiting on ansible-rulebook..."
    sleep 2
  done
fi
