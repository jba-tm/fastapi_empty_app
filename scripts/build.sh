#!/usr/bin/env bash
IFS=
#SECRET_KEY=$(python3 -c 'import random; print("".join(random.SystemRandom().choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for _ in range(50)))')
#
#
#SECRET_KEY=$SECRET_KEY \
docker-compose --env-file ./.env up --detach --build
