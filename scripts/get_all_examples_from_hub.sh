#!/bin/bash
# HF login (TODO)
EXAMPLE_NAMES=(BallChase FPS FlyBy JumperHard Racer)
for EXAMPLE in $EXAMPLE_NAMES; do
    echo $EXAMPLE
    gdrl.load_from_hub -r edbeeching/godot_rl_$EXAMPLE
done