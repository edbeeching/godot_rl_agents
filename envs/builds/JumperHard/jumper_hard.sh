#!/bin/sh
echo -ne '\033c\033]0;JumperHard\a'
base_path="$(dirname "$(realpath "$0")")"
"$base_path/jumper_hard.x86_64" "$@"
