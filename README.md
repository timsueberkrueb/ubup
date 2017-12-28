ubup
====

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![GitHub release](https://img.shields.io/github/release/tim-sueberkrueb/ubup.svg)](https://github.com/tim-sueberkrueb/ubup/releases)
[![GitHub issues](https://img.shields.io/github/issues/tim-sueberkrueb/ubup.svg)](https://github.com/tim-sueberkrueb/ubup/issues)
[![Maintained](https://img.shields.io/maintenance/yes/2017.svg)](https://github.com/tim-sueberkrueb/ubup/commits/develop)

🚀 **Ub**untu set**up** utility.

Automate the steps you run after installing Ubuntu in a declarative way.

## Requirements

* Ubuntu 16.04 or later (Python >= 3.5)

## Configuration

Setup configuration is stored in declarative `setup.yaml` files:

```yaml
folders:
  - ~/Apps
  - ~/Projects
apt-packages:
  - fish
  - cowsay
snap-packages:
  - vscode
  - discord
scriptlets:
  hello: |
    echo "Hello world :D"
scripts:
  - myscript.sh
```

The keys of the top-level dictionary (e.g. `folders`, `apt-packages` ...)
and the schema of the associated values are defined by plugins. There
is a set of [built-in plugins](#built-in-plugins) that ship with ubup. If you cannot find
an existing plugin that fits your need, you can ...

* write your own bash script ...
  * ... inline via the [`scriptlets` plugin](#scriptlets)
  * ... in a seperate file, referencing it using the [`scripts` plugin](#scripts)
* create your own [custom plugin](#custom-plugins)

If you need control over the sequence in which setup instructions are performed,
you can use the alternative step-based schema:

```yaml
steps:
  - folders:
    - ~/Apps
    # ...
  - scripts:
    - download-appimages.sh
    # ...
```

Optionally, you can specify some additional metadata:

```yaml
author: John Doe <john.doe@example.com>
description: |
  Tested on Ubuntu 17.10
  ...
revision: 10
version: '0.1.0'
last_updated: '2017/10/10'
steps: # ...
```

## Perform Setup

To perform your setup, simply run

```
./path/to/ubup/setup
```

in the folder that contains your `setup.yaml`.

## Configuration with Git

By creating a Git repository with your configuration, you can
not only easily host it on your preferred Git hosting service but
you can also add ubup as a Git submodule. This minimizes your
installation steps and ensures you always run with a version
of ubup that you tested your setup against.

Create a new repository:

```
mkdir ubuntu-post-install && cd ubuntu-post-install
git init
```

Add the `ubup` repository as a submodule:

```
# Note: It is recommended to use the master branch to
# ensure you run with a stable version of ubup.
git submodule add -b master https://github.com/tim-sueberkrueb/ubup
git submodule update --init
```

Create your `setup.yaml`.

You can now run `./ubup/setup` inside your repository
to perform your setup.

## Built-in Plugins

### apt-packages

Install a set of packages via `apt`.

```yaml
apt-packages:
  - foo
  - bar
  # ...
```

### folders

Create a set of folders unless they already exist.
You can use `~` or `$HOME` as placeholders for the home directory
and `$USER` as placeholder for the username of the current user.

```yaml
folders:
  - foo
  - bar
  # ...
```

### scriptlets

Run inline bash script snippets.

```yaml
scriptlets:
  hello: |
    echo "Hello World"
  foo: |
    # ...
```

### scripts

Run a set of separate bash scripts.

```yaml
scripts:
  - hello.sh
  - scripts/foo.sh
  - scripts/bar.sh
```

### snap-packages

Install a set of snap packages.

You can either just define the names of the packages to install or provide a
dictionary with additional options in the following schema:
```
<snap-package>:
    <option-key>: <option-value>
```

The following options are supported:

* `classic: <true|false>`: Toggle classic [confinement](https://docs.snapcraft.io/reference/confinement)
* `channel: <track>/<risk level>/<branch>`: [Snap channel](https://docs.snapcraft.io/reference/channels)
* `jailmode <true|false>`: Toggle enforcement of strict [confinement](https://docs.snapcraft.io/reference/confinement)
* `devmode <true|false>`: Toggle developer mode [confinement](https://docs.snapcraft.io/reference/confinement)

```yaml
snap-packages:
  - foo
  - bar:
    classic: true
    channel: latest/stable
    jailmode: false
    devmode: false
```

## Custom Plugins

Custom plugins can be created in a folder called `plugins`
next to the `setup.yaml`.
This folder may contain a set of Python files (`*.py`).
Each Python file may contain one or more
Python classes with a class name ending with `Plugin` (e.g. `BarPlugin`, `MyPlugin`
and even `Plugin` are valid plugin class names).

ubup provides a lightweight plugin API which can be imported using

```python
import ubup.plugins
```

It mainly provides the abstract base class `AbstractPlugin`
which serves as the skeleton for custom (as well as built-in)
plugins.

---

Hint:

```python
from ubup.plugins import AbstractPlugin
```
is equivalent to

```python
from ubup import AbstractPlugin
```

---

**Note:** You should not call your plugin class `AbstractPlugin`.
If you do so, the class will be ignored.

A hello world plugin `plugins/hello-world.py` is as simple as:

```python
from ubup import AbstractPlugin

class HelloPlugin(AbstractPlugin):
    key = 'hello'
    schema = str

    def perform(self):
        print(f"Hello {self.config}!")

```

`key` must be a unique name you will later reference the plugin
by in your `setup.yaml`.

`schema` must be set to a valid Python data structure that
will be validated using the Python [schema library](https://github.com/keleshev/schema).

`perform` must define whatever you want to run when your
plugin is performed.

`self.config` holds the user configuration.

This would be a valid `setup.yaml` for this example plugin:

```yaml
hello: world
```

`self.config` will contain the string `"world"`.

This wouldn't be a valid configuration for this example plugin:

```yaml
hello:
  - a
  - b
  - c
```

because we set `schema = str`.

If you think your plugin could be useful for other users as well,
please feel encouraged to create a pull request to add it as built-in plugin!

The same goes for extending or improving existing plugins, of course.

## Acknowledgements

This software is not endorsed by or affiliated with Ubuntu or Canonical.
Ubuntu and Canonical are registered trademarks of Canonical Ltd.

## License

Licensed unter the terms of the MIT license.
