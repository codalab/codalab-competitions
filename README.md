# CodaLab [![Circle CI](https://circleci.com/gh/codalab/codalab-competitions.svg?style=shield)](https://circleci.com/gh/codalab/codalab-competitions)

## What is CodaLab?

CodaLab is an open-source web-based platform that enables researchers, developers, and data scientists to collaborate, with the goal of advancing research fields where machine learning and advanced computation is used.  CodaLab helps to solve many common problems in the arena of data-oriented research through its online community where people can share worksheets and participate in competitions.

To see Codalab Competition's in action, visit [competitions.codalab.org](https://competitions.codalab.org/).

## Competition's Documentation

- [CodaLab Wiki](https://github.com/codalab/codalab/wiki)

## Community

The CodaLab community forum is hosted on Google Groups.
- [CodaLabDev Google Groups Forum](https://groups.google.com/forum/#!forum/codalabdev)


## Quick installation (for Linux!)

Install docker and add your user to the docker group, if you haven't already

```
$ wget -qO- https://get.docker.com/ | sh

...

$ sudo usermod -aG docker $USER
```

Clone this repo and get the default environment setup
```
$ git clone git@github.com:codalab/codalab-competitions.git
$ cd codalab-competitions
$ cp .env_sample .env
$ pip install docker-compose
$ docker-compose up -d
```

Now you should be able to access http://localhost/
