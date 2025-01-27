![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/deeep-network/ansible_collections/badge)

# Setting Up Local Machine

We leverage pipx to ensure that all programs and librarys we depend on can be installed globally and isolated with venvs out of the box. It's also supported by MacOS, Linux, and Windows.

## Install pipx

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

---

## Setup for Local Virtual Machines

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
