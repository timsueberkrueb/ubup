ubup Development
================

## Requirements

* Ubuntu (16.04 or later)
* Python >= 3.5
  * pip
  * click
  * ruamel.yaml
  * schema
  * progressbar2

On Ubuntu 16.04 or later, run:
```bash
apt-get install python3 python3-pip
pip3 install click ruamel.yaml schema progressbar2
```

## Setup

After installing all requirements and cloning the repository, you can run ubup:
```bash
cd ubup/
python3 main.py <path-to-setup-yaml>
```

## Tests

You need to have [Docker](https://www.docker.com/) or [LXD](https://linuxcontainers.org/)
installed in order to run tests.
Those are required in order to run tests without polluting the host system.

Install LXD it by running:

```bash
snap install lxd
```

and set it up using:


```bash
lxd init
```

Install Docker by running:

```bash
snap install docker
```

Use the `tests/run_tests.py` script to run tests.

Switch between container engines using the `--docker` or `--lxd` command line options.
If you're using docker, you need to run the tests with `--build-docker-images`
at least once.

See `./tests/run_tests.py --help` for more options.

## Contributing

Contributions in form of bug reports, feature proposals or pull requests are highly
appreciated!
