ubup
====

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![GitHub release](https://img.shields.io/github/release/timsueberkrueb/ubup.svg)](https://github.com/timsueberkrueb/ubup/releases)
[![Build Status](https://travis-ci.org/timsueberkrueb/ubup.svg?branch=develop)](https://travis-ci.org/timsueberkrueb/ubup)
[![GitHub issues](https://img.shields.io/github/issues/timsueberkrueb/ubup.svg)](https://github.com/timsueberkrueb/ubup/issues)
[![Maintained](https://img.shields.io/maintenance/yes/2019.svg)](https://github.com/timsueberkrueb/ubup/commits/develop)

🚀 **Ub**untu set**up** utility.

Automate the steps you run after installing Ubuntu in a declarative way.

## Requirements

* Ubuntu 16.04 or later (Python >= 3.5)

Refer to the [development guide](DEVELOPMENT.md) for more information.

## Configuration

Setup configuration is stored in declarative `setup.yaml` files. They consist
of three types of elements: actions, categories and metadata.

### Actions

Categories and metadata are optional features, meaning you can create a
completely valid and functional `setup.yaml` files by using actions only:

```yaml
$folders:
  - ~/Apps
  - ~/Projects
$apt-packages:
  - fish
  - cowsay
$snap-packages:
  - vscode
  - discord
$scriptlet: |
  echo "Hello world :D"
$scripts:
  - myscript.sh
```

As you might have guessed, keys beginning with `$` (e.g. `$folders`,
`$apt-packages`) and their values are called actions. They represent setup
instructions in your configuration.

Their names (or keys), schemata and functionalities are defined by plugins.
There is a set of [built-in plugins](#built-in-plugins) that ship with ubup.

If you cannot find an existing plugin that fits your need, you can ...

* write your own bash script ...
  * inline via the [`scriptlet` plugin](#scriptlet)
  * in a seperate file, referencing it using the [`scripts` plugin](#scripts)
* create your own [custom plugin](#custom-plugins)

Sequence matters in many cases and therefore the order of actions is
preserved when ubup performs your setup.

### Categories

To archive a more organized structure, you can use optional categories.

```yaml
apps:
  $snap-packages:
    - chromium
    - vlc
  appimages:
    foo:
      $scriptlet: |
        # ...
    bar:
      # ...
  # ...
```

All keys that don't start with `$` and that are not metadata keys are
treated as categories. Their main purpose is to support a better structure.

Categories can contain subcategories or actions and the order of categories
is preserved.

### Metadata

Optionally, you can specify some additional metadata:

```yaml
author: John Doe <john.doe@example.com>
description: |
  My personal setup configuration.
  ...
setup:
  foo: # category
    $apt-packages: # action
      # ...
```

Where `setup` contains the root for all categories and actions.
You may not mix metadata with actions or categories and metadata keys
are not allowed to be reused as category names.

Supported metadata keys are:
* `author: <str>`: The author of the configuration file
* `description: <str>`: A description of the configuration file

## Perform Setup

To perform your setup, simply run

```
ubup
```

in the folder that contains your `setup.yaml`.

## Built-in Plugins

### apt-packages

Install a set of packages via `apt`.

```yaml
$apt-packages:
  - foo
  - bar
  # ...
```

### copy

Copy files or folders. This plugin will not create missing target
directories. Use the `folders` plugin to ensure that target directories
exist.
You can use `~` or `$HOME` as placeholders for the home directory
and `$USER` as placeholder for the username of the current user.
Relative paths are relative to the directory containing the `setup.yaml`.

```yaml
$copy:
  source: target
  foo/*.txt: ~/Documents
  test.txt: /opt/foo/bar
```

### flatpak-packages

Install a set of Flatpak packages.

The list may contain the following types of elements:
* `.flatpakref` filename or url
* `.flatpak` filename or url
* A directory for more options:
  * `package: <.flatpakref url or filename>` (required)
  * `remote: <str>`: The remote repository to look for the app or runtime (optional)
  * `target: <system|user>`: Whether to install the flatpak for the
    current user or system-wide (optional, default is `system`)
  * `type: <ref|bundle|app|runtime>`: Whether to look for an app, runtime,
    bundle or ref (optional)
    * `ref`: look for a `.flatpakref` file
    * `bundle`: look for a `.flatpak` bundle
    * `app`: look for an app with the given name in a `remote` repository
    * `runtime`: look for a runtime with the given name in a `remote` repository

```yaml
$flatpak-packages:
  - foo.flatpak
  - bar.flatpakref
  - https://example.com/foo.flatpakref
  - package: https://example.com/bar.flatpakref
    type: ref
    target: user
  - package: org.freedesktop.Platform
    remote: flathub
    type: runtime
```

### flatpak-repositories

Add a set of remote Flatpak repositories.
Each repository is defined as a dictionary with the following keys:
* `name: <str>`: The local name of the repository (required)
* `location: <str>`: Url to a remote `.flatpakrepo` (required)
* `target: <system|user>`: Whether to install the repository for the
  current user or system-wide (optional, default is `system`)

```yaml
$flatpak-repositories:
  - name: flathub
    location: https://flathub.org/repo/flathub.flatpakrepo
    target: system
```


### folders

Create a set of folders unless they already exist.
You can use `~` or `$HOME` as placeholders for the home directory
and `$USER` as placeholder for the username of the current user.

```yaml
$folders:
  - foo
  - bar
  # ...
```

### github-releases

Download GitHub release assets.
Each asset is defined as a dictionary with the following keys:
* `repo: <user>/<repo>`: GitHub repository
* `release`: GitHub release (tag or `latest`)
* `asset`: Asset to download (either the full filename or a regex)
* `target`: Target filename to save the asset as

```yaml
$github-releases:
  - repo: user/repo
    release: v1.2.3
    asset: MyAsset-[0-9.]+.zip
    target: ~/Documents/MyAsset.zip
```

### ppas

Add a set of PPAs unless they are already active.
PPAs must be provided in the format `user/ppa` as opposed to `ppa:user/ppa`
since the action name `$ppas` makes it obvious that the repository to add
is a ppa.

```yaml
$ppas:
  - foo/bar
  - alexlarsson/flatpak
  # ...
```

### scriptlet

Run an inline bash script snippet.

```yaml
$scriptlet: |
    echo "Hello World"
    # ...
```

### scripts

Run a set of separate bash scripts.

```yaml
$scripts:
  - hello.sh
  - scripts/foo.sh
  - scripts/bar.sh
```

### snap-packages

Install a set of snap packages.

You can either just define the names of the packages to install or
provide a dictionary with additional options:

* `package: <str>`: Name of the package to install or `.snap` filename (required)
* `classic: <true|false>`: Toggle classic [confinement](https://docs.snapcraft.io/reference/confinement) (optional)
* `channel: <track>/<risk level>/<branch>`: [Snap channel](https://docs.snapcraft.io/reference/channels) (optional)
* `jailmode: <true|false>`: Toggle enforcement of strict [confinement](https://docs.snapcraft.io/reference/confinement)
  (optional)
* `devmode: <true|false>`: Toggle developer mode [confinement](https://docs.snapcraft.io/reference/confinement) (optional)
* `dangerous: <true|false>`: Install the given snap file even if there are no signatures for it (optional)

```yaml
$snap-packages:
  - foo
  - package: bar
    classic: true
    channel: latest/stable
    jailmode: false
    devmode: false
```

---

Missing something? Create a pull request to add your plugin!

---

## Custom Plugins

Custom plugins can be created in a folder called `plugins`
next to the `setup.yaml`.
This folder may contain a set of Python files (`*.py`).
Each Python file may contain one or more
Python classes with a class name ending with `Plugin` (e.g. `BarPlugin`,
`MyPlugin` and even `Plugin` are valid plugin class names).

**Note:** There is one exception: you may not call your plugin class
`AbstractPlugin`. If you do so, the class will be simply ignored.

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

A hello world plugin `plugins/hello-world.py` is as simple as:

```python
from ubup import AbstractPlugin

class HelloPlugin(AbstractPlugin):
    key = 'hello'
    schema = str

    def perform(self):
        print("Hello {}!".format(self.config))

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
$hello: world
```

`self.config` will contain the string `"world"`.

This wouldn't be a valid configuration for this example plugin:

```yaml
$hello:
  - a
  - b
  - c
```

because we set `schema = str`.

If you think your plugin could be useful for other users as well,
please feel encouraged to create a pull request to add it as built-in plugin!

The same goes for extending or improving existing plugins, of course.

## Remote support (experimental)

ubup has experimental support for performing setups remotely via SSH.

To try it out, run:

```
ubup --remote "user@hostname"
```

This option is basically just a shortcut running the SSH commands you might
run manually to copy ubup and your setup instructions to the remote and to run it.

Therefore there are some limitations:

* Only works properly with password-less logins
* Is disabled when ubup is ran from source

The latter is necessary because ubup temporarily copies itself to the remote machine.

## Acknowledgements

This software is not endorsed by or affiliated with Ubuntu or Canonical.
Ubuntu and Canonical are registered trademarks of Canonical Ltd.

## License

Licensed unter the terms of the MIT license.
