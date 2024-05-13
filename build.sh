#!/usr/bin/env bash

QTSASS_FLAGS=()
WATCH=0

usage () {
  echo "usage: $0 [-h|--help] [-w|--watch] [...qtsass flags]";
  qtsass -h
}

build() {
  if [[ $WATCH -eq 1 ]]; then
    qtsass "$@" "${QTSASS_FLAGS[@]}" &
  else
    qtsass "$@" "${QTSASS_FLAGS[@]}"
  fi
}

options=$(getopt -l "help,watch" -o "hw" -- "$@")
eval set -- "$options"

while true;
do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    -w|--watch)
      QTSASS_FLAGS+=("-w")
      WATCH=1
      shift
      ;;
    --)
      shift
      QTSASS_FLAGS+=("$@")
      break;
  esac
done

(
  trap 'kill 0' SIGINT;

  build scss/OpenLight.scss -o OpenLight/OpenLight.qss
  build scss/OpenLight_Overlay.scss -o OpenLight/overlay/OpenLight_Overlay.qss
  build scss/OpenDark.scss -o OpenDark/OpenDark.qss
  build scss/OpenDark_Overlay.scss -o OpenDark/overlay/OpenDark_Overlay.qss

  wait
)