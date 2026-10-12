#!/usr/bin/env bash
set -euo pipefail

IMAGE="ghcr.io/nps4nps/nps4nps_web"

APP_VERSION="${APP_VERSION:?APP_VERSION not set}"

docker build \
  --tag "$IMAGE:$APP_VERSION" \
  --tag "$IMAGE:latest" \
  .
