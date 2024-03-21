#!/usr/bin/env bash

# This file for demo purposes.

alert="
IMPORTANT:
don't forget to set environment variables HOST_DATA_STORAGE
(it should be a path on your local machine)

The script awaits that you will do it in the ./set_env.local file
content of file for example:
$ cat ./set_env.local
export HOST_DATA_STORAGE=/home/user/data
"

if [ -f "./set_env.local" ]; then
    source ./set_env.local
else
    echo "WARNING: set_env.local not found. Using current directory as HOST_DATA_STORAGE."
    export HOST_DATA_STORAGE=$(pwd)/demo_data
fi

if [ -z "$HOST_DATA_STORAGE" ]; then
    echo "$alert"
    exit 1
fi

chmod -R 754 ./redis
chmod +x ./common/build.sh

DOCKER_COMPOSE_FILE=docker-compose-demo.yml

case "$1" in
    "up")
        echo "Up..."
        ./common/build.sh
        docker-compose -f $DOCKER_COMPOSE_FILE up -d
        ;;
    "down")
        echo "Down..."
        docker-compose -f $DOCKER_COMPOSE_FILE down
        ;;
    "stop")
        echo "Stopping..."
        docker-compose -f $DOCKER_COMPOSE_FILE stop
        ;;
    "start")
        echo "Starting..."
        docker-compose -f $DOCKER_COMPOSE_FILE start
        ;;
    "rm")
        echo "Removing..."
        docker-compose -f $DOCKER_COMPOSE_FILE rm -f -s -v
        ;;
    *)
        echo "Usage: ./${0##*/} {build|build-frontend|up|down|stop|start|rm}"
        echo "
up - up the microservices (similar: docker-compose up -d)
down - down the microservices (similar: docker-compose down)
stop - stop the microservices (similar: docker-compose stop)
start - start the microservices (similar: docker-compose start)
rm - remove the microservices (similar: docker-compose rm -f -s -v)
"
        ;;
esac
