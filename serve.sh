#!/usr/bin/env sh

# Create `exo-alma` network if needed
if [ "$(docker network ls --quiet --filter name=exo-alma | wc -c)" -eq 0 ]; then
  docker network create exo-alma
fi

# Remove older `alma` container if there's one
if [ "$(docker container ls --quiet --all --filter name=alma | wc -c)" -ne 0 ]; then
  docker rm alma 2>&1 /dev/null
fi

PORT=${PORT:-5000}
docker build -t alma:fake . && docker run -it --network exo-alma -e PORT=$PORT -p $PORT:$PORT --name=alma -v "$PWD/src":/usr/src/app alma:fake
