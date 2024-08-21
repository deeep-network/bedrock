## Presearch playbooks
=========\
Instal and start presearch node software.\
Environment variables:
  - **docker_container_version** - version of the [dockerhub image](https://hub.docker.com/r/presearch/node/tags)(current 1.2.34). 
  - **presearch_reg_code**  - registration code of client from preserch service.
 
```
 sudo ansible-playbook ./services/roles/presearch/presearch-install.yml --extra-vars "presearch_reg_code=<registration_code>" -vvv
```
Stop docker container:
```
 sudo ansible-playbook ./services/roles/presearch/presearch-stop.yml 
```
Start docker container:
```
sudo ansible-playbook ./services/roles/presearch/presearch-start.yml --extra-vars "presearch_reg_code=<registration_code>" -vvv
```
Uninstall docker and all dependencies:
```
sudo ansible-playbook ./services/roles/presearch/presearch-uninsatall.yml 
```
Update docker container version:\
Environment variables:
  - **docker_container_version** - version of the [dockerhub image](https://hub.docker.com/r/presearch/node/tags)(current 1.2.34). 
```
sudo ansible-playbook ./services/roles/presearch/presearch-update.yml --extra-vars "presearch_reg_code=<registration_code>" -vvv
```
 
