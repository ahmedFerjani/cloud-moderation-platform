#!/bin/bash

set -e

rm -rf python layer.zip
mkdir -p python

docker run --platform linux/arm64 \
  -v "$PWD":/var/task \
  -w /var/task \
  public.ecr.aws/sam/build-python3.12 \
  bash -c "pip install -r requirements.txt --no-cache-dir -t python"

zip -r layer.zip python 