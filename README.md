# pymola

A python/modelica based simulation environment.

[![Build Status](https://travis-ci.org/jackvreeken/pymola.svg)](https://travis-ci.org/jackvreeken/pymola)
[![Build status](https://ci.appveyor.com/api/projects/status/7spiw3or4qpm40cw/branch/master?svg=true)](https://ci.appveyor.com/project/jackvreeken/pymola/branch/master)
[![Coverage Status](https://coveralls.io/repos/github/jackvreeken/pymola/badge.svg?branch=master)](https://coveralls.io/github/jackvreeken/pymola?branch=master)


## Install

1. Install anaconda 3.

2. Setup environment.

```bash
./create_conda_env.sh enduser
. activate pymola
jupyter notebook
```

## Examples
[Simple IPython Notebook Example](test/Spring.ipynb)

## Roadmap

### Completed Tasks

* hello world compilation
* Project setup.
* Unit testing for parsers.
* Parsing basic hello world example.
* Travis continuous integration testing setup.
* Coveralls coverage testing setup.

### TODO

* add more complicated test cases
* resolve grammar issues
* support more of modelica language
* add modelica magic support for ipython?

<!--- vim:ts=4:sw=4:expandtab:
!-->
