#!/usr/bin/env bash
BASE_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )/../src/"



docker-compose up --build && bash



