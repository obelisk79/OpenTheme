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

  build ./scss/OpenTheme.scss -o ./OpenDark/OpenTheme.qss
  build ./scss/OpenTheme_Overlay.scss -o ./OpenDark/overlay/OpenTheme_Overlay.qss

  # token files for every pack, the variant packs' .cfg, and package.xml
  python3 ./tools/make_themes.py

  wait
)
