NPs4NPs
=========

Contents
-----------------
- [Overview](#overview)
- [Quickstart Guide](#quickstart-guide)
- [Attribution](#attribution)
- [For Developers](#for-developers)

## Overview

This repository contains the source code for the Nanopublications for Natural Products (NPs4NPs) project's web application.

The web app focuses on two services:

- Provide an API to allow validating literals sent for verifications from nanodash instances
- Provide querying and visualization options to users consuming the nanopublications generated in the NPs4NPs project.

## Quickstart guide

While the [MITE Database](https://mite.bioinformatics.nl/) is primarily intended to be used online, it can also be used offline.

### Installation Guide

*Nota bene: while this application should work on any OS, it has only been tested on Ubuntu Linux 20.04 and 22.04.*

Assuming that Docker is installed:

```commandline
docker run -p 8000:8000 ghcr.io/nps4nps/nps4nps_web:latest
```

You can now use the app running on http://127.0.0.1:8000/.

## Attribution

### License

`mite_web` is an open source tool licensed under the MIT license (see [LICENSE](LICENSE)).

### Publications

TBA

### Acknowledgements

TBA

## For Developers

### Application logic

*Nota bene: while this application should work on any OS, it has only been tested on Ubuntu Linux 20.04 and 22.04.*

Since `mite_web 2.0.0`, the application follows 12-factor-app principles. 

All data is being queried from the nanopublications server network. Therefore, the app itself is stateless.

All parameters are provided as environment variables. 

### Development build

This build simplifies development by hot reloading (recursively watching directories for changes).
Variables are read from an .env file (see [.env.example](.env.example)).

#### Installation

*Nota bene: assumes that `uv` is installed.*

1. Download and install dependencies
```commandline
git@github.com:nps4nps/nps4nps_web.git
uv sync --extra dev
uv run prek install -f
```

2. Run tests
```commandline
uv run pytest
```
Tests will also run via `prek` and GitHub Actions on PRs into main

3Run docker compose
```commandline
docker compose -f dev-compose.yml build
docker compose -f dev-compose.yml up --watch
```

You can now use the database running on http://127.0.0.1:8000/.

Sometimes, the hot reloading doesn't work perfectly (e.g. dependency updates).
In these cases, terminate with `ctrl+c` and rebuild.

#### Deployment Checklist

*Nota bene: releases must be prepared locally to update the `uv.lock` file; else, builds fail.*

The main software artifact produced by this repo are Docker containers deposited in the GitHub Container Repository.
These containers are created automatically via GitHub Actions on every new Release.

There are two "types" of releases for Mite Web

### Production build

*Nota bene: production build should be exclusively deployed from Docker images (e.g. from [GHCR](ghcr.io/nps4nps/nps4nps_web:latest))*

The app requires certain parameters to be run in production mode.
These parameters should be provided as environment variables as specified by the respective platform provider.
An example can be found in [.env.example](.env.example).

If parameters are not provided, the application will automatically start in development mode.


#### lisc.univie.ac.at

- Download the content of the [lisc](production/lisc) directory (e.g. with `curl --output <filename> <URL>`)
- Specify the desired container version in [compose.yml](production/lisc/compose.yml)
- Add parameters in an `.env` file (see [.env.example](.env.example)
- Run `docker compose -f compose.yml up`