![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/deeep-network/ansible_collections/badge)

# Development

## Install pipx

We leverage pipx to ensure that all programs and librarys we depend on can be installed globally and isolated with venvs out of the box. It's also supported by MacOS, Linux, and Windows.

### MacOS

```bash
brew install pipx
```

### Linux

```bash
apt install pipx
```

### More

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

We leverage the ability for Molecule to manage and control local VM's using a virtualization software of choice.

On the DeEEP Device - the Ansible Controller is the Device itself which then pushes to the individually managed VM's within Incus. Each VM also becomes and independent Ansible Controller. This setup requires every role to be `localhost` orientated. Allowing VMs the ability to configure themselves when necessary.

> [!NOTE] For testing, we skip the Incus layer. Meaning the Ansible Controller for tests is your local machine. Pushing directly to the VM running locally. This is meant to simplify the process. Especially since MacOS support for Incus in a VM doesn't work as intended.

### linux/windows

#### [multipass](https://multipass.run/install)

> intel Macs can also use this method

### macos

#### [orbstack](https://docs.orbstack.dev/install)

```bash
brew install orbstack
```

### linux/windows/macos

#### [UTM](https://mac.getutm.app/)

```bash
brew install --cask utm
```

## Using Molecule

---

2. set the `MOLECULE_SUBSTRATE` environment variable to the one of your choice

    > If you've already ran molecule before updating this variable you may need to use `molecule destroy` or `molecule reset` for it to take effect

3. Setup Pulumi ESC

    1. Install [Pulumi ESC](https://www.pulumi.com/docs/esc/download-install/)

    2. Install [Direnv](https://direnv.net/docs/installation.html)

    3. Login to Pulumi ESC - request access to `deeep-network/dev/services` (DM @anthonyra)

    4. run `direnv allow .` in root directory

4. test **all** services

    ```bash
    molecule converge
    ```

5. test an **individual** service

    ```bash
    molecule converge -- -e='fqcn=test.yml'
    molecule converge -- -e='fqcn=test'
    molecule converge -- -e='fqcn=depin.services.test'
    molecule converge -- -e=@tasks/vars/services/test.yml
    ```

6. test **all** libs

    ```bash
    molecule converge -s libs
    ```

7. test an **individual** lib

    ```bash
    molecule converge -s libs -- -e='fqcn=depin.libs.test'
    molecule converge -s libs -- -e=@tasks/vars/libs/test.yml
    ```
