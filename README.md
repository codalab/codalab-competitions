![CodaLab logo](codalab/apps/web/static/img/codalab-logo-fullcolor-positive.png) [![Circle CI](https://circleci.com/gh/codalab/codalab-competitions.svg?style=shield)](https://circleci.com/gh/codalab/codalab-competitions)
[![codecov](https://codecov.io/gh/codalab/codalab-competitions/branch/setup-github-actions-pytest/graph/badge.svg)](https://codecov.io/gh/codalab/codalab-competitions)



## What is CodaLab?

CodaLab is an open-source web-based platform that enables researchers, developers, and data scientists to collaborate, with the goal of advancing research fields where machine learning and advanced computation is used.  CodaLab helps to solve many common problems in the arena of data-oriented research through its online community where people can share worksheets and participate in competitions.

To see Codalab Competition's in action, visit [codalab.lisn.fr](https://codalab.lisn.fr/).

## Documentation

- [CodaLab Wiki](https://github.com/codalab/codalab/wiki)

## Community

The CodaLab community forum is hosted on Google Groups.
- [CodaLab Competitions Google Groups Forum](https://groups.google.com/forum/#!forum/codalab-competitions)


## Quick installation (for Linux!)

_To participate in competitions, or even organize your own competition, **you don't need to install anything**, you just need to sign in an instance of the platform (e.g. [this one](https://codalab.lisn.fr/)). 
If you wish to configure your own instance of CodaLab competitions, here are the instructions:_

Install docker and add your user to the docker group, if you haven't already

```
$ wget -qO- https://get.docker.com/ | sh
$ sudo usermod -aG docker $USER
```

Clone this repo and get the default environment setup
```
$ git clone https://github.com/codalab/codalab-competitions
$ cd codalab-competitions
$ cp .env_sample .env
$ pip install docker-compose
$ docker-compose up -d
```

Now you should be able to access http://localhost/

**More details on how to configure your own instance:**
- [Configure Codalab from scratch](https://github.com/codalab/codalab-competitions/wiki/Setup-Local-Competitions#user-content-get-the-source-code)
- [Set up data storage](https://github.com/codalab/codalab-competitions/wiki/Storage)


## License

Copyright (c) 2013-2015, The Outercurve Foundation.
Copyright (c) 2016-2021, Université Paris-Saclay.
This software is released under the Apache License 2.0 (the "License"); you may not use the software except in compliance with the License.

The text of the Apache License 2.0 can be found online at:
http://www.opensource.org/licenses/apache2.0.php

## Cite CodaLab Competitions in your research

```
@article{codalab_competitions,
    author = {Adrien Pavao and Isabelle Guyon and Anne-Catherine Letournel and Xavier Baró and 
              Hugo Escalante and Sergio Escalera and Tyler Thomas and Zhen Xu},
    title = {CodaLab Competitions: An open source platform to organize scientific challenges},
    url = {https://hal.inria.fr/hal-03629462v1},
    year = {2022},
    journal = {Technical report}
}
```
