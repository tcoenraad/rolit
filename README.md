Rolit
=====

[![Build Status](https://travis-ci.org/tcoenraad/rolit.png?branch=master)](https://travis-ci.org/tcoenraad/rolit)
[![Code Health](https://landscape.io/github/tcoenraad/rolit/master/landscape.png)](https://landscape.io/github/tcoenraad/rolit/master)

a Rolit server for softwaresystemen - Python edition

Requirements
============
- Install [pip](http://www.pip-installer.org/en/latest/installing.html)

How to set-up
=============

    $ sudo apt-get install python-m2crypto
    $ sudo pip install -r requirements.txt

How to run
==========

Run server:

    $ python bin/server.py <port = 3535>
    
Run tests:

    $ py.test

Run tests with coverage:

    $ py.test --cov rolit tests/ 
