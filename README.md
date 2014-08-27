# CodaLab [![Build Status](https://travis-ci.org/codalab/codalab.png?branch=master)](https://travis-ci.org/codalab/codalab)

## What is CodaLab?
CodaLab is an open-source web-based platform that enables researchers, developers, and data scientists to collaborate, with the goal of advancing research fields where machine learning and advanced computation is used.  CodaLab helps to solve many common problems in the arena of data-oriented research through its online community where people can share worksheets and participate in competitions.

To see CodaLab in action, visit [www.codalab.org](http://www.codalab.org).

## Documentation
- [CodaLab Wiki](https://github.com/codalab/codalab/wiki)
- [CodaLab Online Help](http://www.codalab.org/help)

## Community
The CodaLab community forum is hosted on Google Groups.
- [CodaLabDev Google Groups Forum](https://groups.google.com/forum/#!forum/codalabdev)

## Quickstart
Run the following commands once to set everything up in Linux:

		./dev_setup.sh
		cd codalab
		cp codalab/settings/local_sample.py codalab/settings/local.py
		./manage syncdb --migrate
		./manage config_gen

After that, run the following to start the server:

		./runserver 0.0.0.0:8000
