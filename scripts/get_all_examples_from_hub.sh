#!/bin/bash
# HF login (TODO)
EXAMPLE_NAMES=(BallChase FPS FlyBy JumperHard Racer Ships Racer ItemSortingCart AirHockey "3DCarParking" DownFall) 
for EXAMPLE in ${EXAMPLE_NAMES[@]}; do
    echo "Downloading example: $EXAMPLE"
    gdrl.env_from_hub -r edbeeching/godot_rl_$EXAMPLE

    chmod +x examples/godot_rl_$EXAMPLE/bin/$EXAMPLE.x86_64
done