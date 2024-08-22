## Hychain playbooks
=========\
Instal and start Hychain node software. Hychain will run as systemd service.\
Environment variables:

  - **guardian_private_key**  - private key of client to start hychain software.

```
 sudo ansible-playbook ./services/roles/hychain/hychain-install.yml --extra-vars "guardian_private_key=<guardian_private_key>" -vvv
```
Stop hychain.service:
```
 sudo ansible-playbook ./services/roles/Hychain/Hychain-stop.yml 
```
Start hychain.service:
```
sudo ansible-playbook ./services/roles/hychain/hychain-start.yml
```
Uninstall hychain.service and all dependencies:
```
sudo ansible-playbook ./services/roles/hychain/hychain-uninsatall.yml 
```
Update hychain.service version. This paybook will delete current version of [hychain](https://github.com/HYCHAIN/guardian-node-software) and pull new one.\
Environment variables:
  - **guardian_private_key** - private key of client to start hychain software.
```
sudo ansible-playbook ./services/roles/hychain/hychain-update.yml --extra-vars "guardian_private_key=<guardian_private_key>" -vvv
 
