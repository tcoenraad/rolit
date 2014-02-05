Rolit
=====

[![Build Status](https://travis-ci.org/tcoenraad/rolit.png?branch=master)](https://travis-ci.org/tcoenraad/rolit)
[![Code Health](https://landscape.io/github/tcoenraad/rolit/master/landscape.png)](https://landscape.io/github/tcoenraad/rolit/master)

a Rolit server for Softwaresystemen - Python edition

Requirements
============
- [Python 2.7](http://www.python.org/download/releases/2.7/)
- [pip](http://www.pip-installer.org/en/latest/installing.html)
- For [pycrypto](https://pypi.python.org/pypi/pycrypto) you need, depending on your OS, `python-dev` or other build tools

How to set-up
=============

    $ sudo pip install -r requirements.txt

How to run
==========

Run server:

    $ python bin/server.py

Run client:

    $ python bin/client.py [host = localhost [port = 3535 [player_name = Monitor_[0-3535] [private_key_file=./private_key]]]]
    
Run tests:

    $ py.test

Run tests with coverage:

    $ py.test --cov rolit tests/ 

Screenshot
==========

![screenshot](http://i.imgur.com/VeJ6qvp.png)
