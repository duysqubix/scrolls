#!/bin/bash

# build image
docker build -t scrolls_test:latest .

# run docker image
docker run scrolls_test:latest