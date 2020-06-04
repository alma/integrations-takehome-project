#!/usr/bin/env sh

docker build -t alma:fake . && docker run -p 5000:5000 -v "$PWD/src":/usr/src/app alma:fake
