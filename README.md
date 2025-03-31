![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/deeep-network/ansible_collections/badge)

# Overview
Developing with bedrock requires a virtual machine, a habitat account, and other dependencies. 
- [Overview](#overview)
- [Virtual Machine Setup](#virtual-machine-setup)
  - [Background](#background)
    - [macos (apple silicon)](#macos-apple-silicon)
      - [orbstack - docs](#orbstack---docs)
    - [linux/windows/macos (intel)](#linuxwindowsmacos-intel)
      - [multipass - docs](#multipass---docs)
    - [linux/windows/macos](#linuxwindowsmacos)
      - [UTM - docs](#utm---docs)
- [Create Chef Habitat Account](#create-chef-habitat-account)
    - [Create a Habitat Builder Account](#create-a-habitat-builder-account)
    - [Create an Origin](#create-an-origin)
    - [Create Personal Access Token](#create-personal-access-token)
- [Install pipx](#install-pipx)
    - [MacOS](#macos)
    - [Linux](#linux)
    - [Other Install Methods](#other-install-methods)
  - [Install Ansible](#install-ansible)
  - [Verify Ansible collections](#verify-ansible-collections)
  - [Install Molecule](#install-molecule)
  - [Post Installation](#post-installation)
- [Getting Started](#getting-started)
- [Next Steps](#next-steps)

# Virtual Machine Setup
You'll need to install virtualization software to run and develop on a virtual machine created by bedrock.

## Background
On the DeEEP Device - the main Ansible Controller is the Device itself which in turn can manage the VM's (via Incus). Each VM is also an independent Ansible Controller for itself. This setup requires every role to be `localhost` first when developed. This isn't the normal way Ansible is meant to be used (push model) so there are some gotchas and things we do that are slightly out of the norm. Being `localhost` first however provides the VMs the ability to configure themselves when necessary. It's also important to note that if it works via `localhost` it will always work being pushed (not always the case in reverse).

> [!NOTE] For testing, we skip the Incus layer. Meaning the Ansible Controller for tests is your local machine (acting like the Device). Pushing directly to the VM running locally (managed by Orbstack, multipass, KVM, or LXD). This is meant to simplify the testing process. Especially since MacOS support for intel based CPU architecture is not well supported.

As such, depending on your development environment pick the most convenient virtualization software. Usually based on OS and CPU

---

### macos (apple silicon)

#### orbstack - [docs](https://docs.orbstack.dev/install)

```bash
brew install orbstack
```

---

### linux/windows/macos (intel)

#### multipass - [docs](https://multipass.run/install)

```bash
brew install --cask multipass
```

```bash
snap install multipass
```

---

### linux/windows/macos

> not well tested, tread carefully

#### UTM - [docs](https://mac.getutm.app/)

```bash
brew install --cask utm
```

# Create Chef Habitat Account
### Create a Habitat Builder Account

For local development of Chef Habitat packages you’ll want to create your own Chef Habitat Builder account. It’s similar to a GitHub or a Docker repo, but stores Habitat Packages. (.hart files)

Set up your builder account at [bldr.habitat.sh](http://bldr.habitat.sh). (You’ll need a GitHub account to sign up)

### Create an Origin

Once signed into your habitat builder account, create a new origin by clicking the ‘Create Origin’ button. This origin will be used for local development of habitat packages.

Name your origin (perhaps use your full name). Set to “Private artifacts” and click “Save & Continue”

### Create Personal Access Token

Head to your profile and create an personal access token. Set this token to the environment on your host machine.

```bash
export HAB_AUTH_TOKEN='your-token-here'
```

# Install pipx

We leverage pipx to ensure that all programs and librarys we depend on can be installed globally and isolated with venvs out of the box. It's also supported by MacOS, Linux, and Windows.

### MacOS

```bash
brew install pipx
```

### Linux

```bash
apt install pipx
```

### Other Install Methods

> https://pipx.pypa.io/stable/installation/

## Install Ansible

```bash
pipx install ansible-core
pipx inject ansible-core psutil netaddr pytz prometheus-client
```

```bash
pipx install ansible-lint
```

## Verify Ansible collections

```bash
pipx install --include-deps ansible-sign
```

## Install Molecule

```bash
pipx install --include-deps molecule
```

## Post Installation

```bash
pipx ensurepath
```

> You can either log out and log back in to your shell or run the following command to refresh your PATH

```bash
source ~/.bashrc
or
source ~/.zshrc
```



# Getting Started

> **Important**: Before proceeding, ensure you have set your `HAB_AUTH_TOKEN` environment variable. This token is required for authenticating with the Habitat Builder service and is expected to be set before continuing.
>
> ```bash
> export HAB_AUTH_TOKEN='your-token-here'
> ```

From the root of the bedrock repo run the following command:

```bash
molecule create
```

This will create the virtual machine and install the needed dependencies.

# Next Steps

Develop a new service with [coral-reef](https://github.com/deeep-network/coral-reef)


