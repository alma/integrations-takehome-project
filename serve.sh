#!/usr/bin/env sh

PORT=${PORT:-5000}
docker build -t alma:fake . && docker run -it -e PORT=$PORT -p $PORT:$PORT -v "$PWD/src":/usr/src/app alma:fake
