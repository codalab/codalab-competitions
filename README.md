![CodaLab logo](codalab/apps/web/static/img/codalab-logo-fullcolor-positive.png) [![Circle CI](https://circleci.com/gh/codalab/codalab-competitions.svg?style=shield)](https://circleci.com/gh/codalab/codalab-competitions)
[![codecov](https://codecov.io/gh/codalab/codalab-competitions/branch/develop/graph/badge.svg)](https://codecov.io/gh/codalab/codalab-competitions)



## What is CodaLab?

CodaLab is an open-source web-based platform that enables researchers, developers, and data scientists to collaborate, with the goal of advancing research fields where machine learning and advanced computation is used.  CodaLab helps to solve many common problems in the arena of data-oriented research through its online community where people can share worksheets and participate in competitions.

To see Codalab Competition's in action, visit [codalab.lisn.fr](https://codalab.lisn.fr/).

_[Codabench](https://github.com/codalab/codabench), the next-gen of CodaLab Competitions, is out. [Try it out](https://www.codabench.org/)!_

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
@article{codalab_competitions_JMLR,
  author  = {Adrien Pavao and Isabelle Guyon and Anne-Catherine Letournel and Dinh-Tuan Tran and Xavier Baro and Hugo Jair Escalante and Sergio Escalera and Tyler Thomas and Zhen Xu},
  title   = {CodaLab Competitions: An Open Source Platform to Organize Scientific Challenges},
  journal = {Journal of Machine Learning Research},
  year    = {2023},
  volume  = {24},
  number  = {198},
  pages   = {1--6},
  url     = {http://jmlr.org/papers/v24/21-1436.html}
}
```
