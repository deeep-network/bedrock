![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/deeep-network/ansible_collections/badge)

# Development

### macos

```bash
brew install pipx
```

### linux

```bash
apt install pipx
```

> https://pipx.pypa.io/stable/installation/

## install ansible

```bash
pipx install ansible-core
pipx inject ansible-core requests pynetbox pyutils pytz netaddr
pipx install ansible-lint
```

```bash
pipx install --include-deps molecule
```

```bash
pipx install --include-deps ansible-sign
```

## Molecule Setup

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

2. set the `MOLECULE_SUBSTRATE` environment variable to the one of your choice

> If you've already ran molecule before updating this variable you may need to use `molecule destroy` or `molecule reset` for it to take effect

3. copy the `example.env` to `.env` and update with the required secrets
