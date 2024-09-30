![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/deeep-network/ansible_collections/badge)

# Development

## Install pipx

### macos

```bash
brew install pipx
```

### linux

```bash
apt install pipx
```

> https://pipx.pypa.io/stable/installation/

## Install Ansible

```bash
pipx install ansible-core
pipx inject ansible-core requests pynetbox pyutils pytz netaddr
pipx install ansible-lint
sudo pip install pynetbox

```

```bash
pipx install --include-deps ansible-sign
```

## Molecule Setup

```bash
pipx install --include-deps molecule
```

### linux/windows

1. install [multipass](https://multipass.run/install)

> intel Macs can also use this method

### macos

1. install [orbstack](https://docs.orbstack.dev/install)

    ```bash
      brew install orbstack
    ```

### experimental

1. install [UTM](https://mac.getutm.app/)

    ```bash
      brew install --cask utm
    ```

## Using Molecule

---

2. set the `MOLECULE_SUBSTRATE` environment variable to the one of your choice

    > If you've already ran molecule before updating this variable you may need to use `molecule destroy` or `molecule reset` for it to take effect

3. copy the `example.env` to `.env` and update the contents

4. test all services

    ```bash
    molecule converge
    ```

5. test individual service role

    ```bash
    molecule converge -- -e='fqcn=test.yml'
    molecule converge -- -e='fqcn=test'
    molecule converge -- -e='fqcn=depin.services.test'
    molecule converge -- -e=@tasks/vars/services/test.yml
    ```

6. test all libs role

    ```bash
    molecule converge -s libs
    ```

7. test individual libs role

    ```bash
    molecule converge -s libs -- -e='fqcn=depin.libs.test'
    molecule converge -s libs -- -e=@tasks/vars/libs/test.yml
    ```
