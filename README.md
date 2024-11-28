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
pipx inject ansible-core requests pynetbox pyutils pytz netaddr
```

```bash
pipx install ansible-lint

```

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

> You can either log out of the shell and log back in or run the following command to refresh your PATH

```bash
source ~/.bashrc
or
source ~/.zshrc
```

---

## Setup for Local Virtual Machines

On the DeEEP Device - the main Ansible Controller is the Device itself which in turn can manage the VM's (via Incus). Each VM is also an independent Ansible Controller for itself. This setup requires every role to be `localhost` first when developed. This isn't the normal way Ansible is meant to be used (push model) so there are some gotchas and things we do that are slightly out of the norm. Being `localhost` first however provides the VMs the ability to configure themselves when necessary. It's also important to not that if it works via `localhost` it will always work being pushed (not always the case in reverse).

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

#### UTM - [docs](https://mac.getutm.app/)

```bash
brew install --cask utm
```

---

## Using Molecule

1. set the `MOLECULE_SUBSTRATE` environment variable to the one of your choice

    > If you've already ran molecule before updating this variable you may need to use `molecule destroy` or `molecule reset` for it to take effect

2. Setup Pulumi ESC

    1. Install [Pulumi ESC](https://www.pulumi.com/docs/esc/download-install/)

    2. Install [Direnv](https://direnv.net/docs/installation.html)

    3. Login to Pulumi ESC - request access to `deeep-network/dev/services` (DM @anthonyra)

    4. run `direnv allow .` in root directory

3. test **all** services

    ```bash
    molecule converge
    ```

4. test an **individual** service

    ```bash
    molecule converge -- -e='fqcn=test'
    molecule converge -- -e='fqcn=depin.services.test'
    ```

5. test **all** libs

    ```bash
    molecule converge -s libs
    ```

6. test an **individual** lib

    ```bash
    molecule converge -s libs -- -e='fqcn=test'
    molecule converge -s libs -- -e='fqcn=depin.libs.test'
    ```
