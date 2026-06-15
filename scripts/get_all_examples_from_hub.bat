REM HF login (TODO)

set EXAMPLE_NAMES=BallChase FPS FlyBy JumperHard Racer Ships Racer ItemSortingCart AirHockey "3DCarParking" DownFall

for %%E in (%EXAMPLE_NAMES%) do (
    echo Downloading example: %%E
    REM Assuming 'gdrl.env_from_hub' is a command you have set up on your system
    gdrl.env_from_hub -r edbeeching/godot_rl_%%E

    REM Skipping the chmod equivalent, as it's not required in Windows
    REM If execution permission needed for binaries, consider icacls or similar.
)

pause
