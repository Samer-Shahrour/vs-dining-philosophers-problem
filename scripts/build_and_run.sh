#!/usr/bin/env bash
export DOCKER_SCOUT=disable
BASE_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )/../src/"

while getopts "n:" opt; do
  case $opt in
    n) number=$OPTARG ;;
    *) echo "Invalid option"; exit 1 ;;
  esac
done

NUMBER_PHILOSOPHERS=${number:-3}

if [ "$NUMBER_PHILOSOPHERS" -lt 2 ]; then
    echo "The number is less than 2. Setting it to 3 by default."
    NUMBER_PHILOSOPHERS=2
fi

function build_container() {
  local dir=$1
  local tag=$2

  echo "Building $tag..."
  if docker build --quiet "${BASE_DIR}${dir}" -t "$tag" >nul 2>&1; then
    echo "Successfully built: $tag"
  else
    echo "Failed to build: $tag" >&2
    exit 1
  fi
  echo ""
}


echo "Checking if network vs-net exists..."
docker network inspect vs-net >/dev/null 2>&1 || docker network create vs-net
echo "Network vs-net is ready."

build_container "philosoph" "philosoph"
build_container "fork" "fork"
build_container "dashboard" "dashboard"

echo "Starting MQTT Broker..."
if docker run -d -p 127.0.0.1:8883:1883 --net=vs-net --name mqttbroker eclipse-mosquitto:1.6.13 >nul 2>&1; then
  echo "MQTT Broker started."
else
  echo "Failed to start MQTT Broker." >&2
  exit 1
fi

function run_container() {
  local name=$1
  local image=$2
  local options=${3:-""}

  echo "Starting $name..."
  if docker run -d --net=vs-net --name "$name" $options "$image" >nul 2>&1; then
    echo "$name started successfully."
  else
    echo "Failed to start $name." >&2
    exit 1
  fi
  echo ""
}

run_container "dashboard" "dashboard" "-p 127.0.0.1:1880:1880"

for i in $(seq 1 ${NUMBER_PHILOSOPHERS});
do
    echo "Starting fork $i..."
    run_container "f$i" "fork" "-e ID=$i"
done

for i in $(seq 1 ${NUMBER_PHILOSOPHERS});
do
    echo "Starting philosoph $i..."
    run_container "ph$i" "philosoph" "-e ID=$i -e NUMBER_PHILOSOPHERS=$NUMBER_PHILOSOPHERS"
done

for i in $(seq 1 ${NUMBER_PHILOSOPHERS});
do
    docker logs -f ph$i &
done


DASHBOARD_URL="http://127.0.0.1:1880/ui"
DASHBOARD_URL_flow="http://127.0.0.1:1880/"

start $DASHBOARD_URL_flow
start $DASHBOARD_URL
