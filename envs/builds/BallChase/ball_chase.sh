#!/bin/sh
echo -ne '\033c\033]0;BallChase\a'
base_path="$(dirname "$(realpath "$0")")"
"$base_path/ball_chase.x86_64" "$@"
