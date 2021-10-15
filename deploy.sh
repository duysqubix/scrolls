#!/bin/bash

IMAGE_NAME_DEV="${SCROLLSDEV_IMAGE_NAME:=eagledaddy/scrolls:dev}"
IMAGE_NAME_PROD="${SCROLLSPROD_IMAGE_NAME:=eagledaddy/scrolls:latest}"

ORIG_BRANCH=$(git branch --show-current)

if [[ "$1" = "dev" ]]; then
    git pull origin dev
    git checkout dev
    echo "building dev image and deploying to docker, ${IMAGE_NAME_DEV}"
    docker build -t $IMAGE_NAME_DEV . && docker push $IMAGE_NAME_DEV

elif [[ "$1" = "prod" ]]; then
    git pull origin master
    git checkout master
    echo "building production image and deploying to docker, , ${IMAGE_NAME_PROD}"
    docker build -t $IMAGE_NAME_PROD . && docker push $IMAGE_NAME_PROD
else
    echo "not a valid option"
fi

git checkout $ORIG_BRANCH

