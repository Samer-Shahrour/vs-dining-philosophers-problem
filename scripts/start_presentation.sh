#!/usr/bin/env bash
export DOCKER_SCOUT=disable
BASE_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )/../src/"


NUMBER_PHILOSOPHERS=${number:-5}
IP="10.8.1.6"


function build_container() {
  local dir=$1
  local tag=$2

  echo "Building $tag..."
  if docker build --quiet "${BASE_DIR}${dir}" -t "$tag"; then
    echo "Successfully built: $tag"
  else
    echo "Failed to build: $tag" >&2
  fi
  echo ""
}
build_container "presentation" "presentation"
build_container "dashboard" "dashboard"


if docker run -d -p 127.0.0.1:8883:1883 --net=vs-net --name mqttbroker eclipse-mosquitto:1.6.13; then
  echo "MQTT Broker started."
fi

if docker run -d -p 127.0.0.1:1880:1880 --net=vs-net --name dashboard dashboard; then
  echo "Dashboard started."
fi

if docker run -d -p 42888:42888 --ip 20.0.1.200 --net=vs-net -e IP=$IP --name presentation presentation; then
  echo "Presentation started."
fi




DASHBOARD_URL="http://127.0.0.1:1880/ui"
DASHBOARD_URL_flow="http://127.0.0.1:1880/"

start $DASHBOARD_URL_flow
start $DASHBOARD_URL