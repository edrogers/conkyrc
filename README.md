Conky configuration files
=========================

These are my Conky configuration files.

![Conky](https://github.com/edrogers/conkyrc/raw/master/screenshot.png)


Installation
------------

Fetch the configuration files from GitHub repository:

```sh
git clone git://github.com/edrogers/conkyrc.git ~/.conky
```

Create link:

```sh
ln -s ~/.conky/conkyrc ~/.conkyrc
```

Install package

```sh
python3 -m pip install .
```

or, for pyenv+pipx usage:

```sh
PYENV_VERSION=3.10.7 pipx install .
```


Enjoy!

Features
--------

* weather with forecast
* CPU graph
* memory graph
* network graph
* processes 

