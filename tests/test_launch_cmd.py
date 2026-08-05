from godot_rl.core.godot_env import GodotEnv


def build(**overrides):
    kwargs = dict(
        env_path="game.x86_64",
        port=11008,
        show_window=True,
        framerate=None,
        seed=0,
        action_repeat=None,
        speedup=None,
    )
    kwargs.update(overrides)
    return GodotEnv._build_launch_cmd(**kwargs)


def test_no_argument_carries_an_embedded_space():
    # Popen receives argv as a list, so a token like "--fixed-fps 60" reaches Godot as a
    # single unknown parameter and the engine aborts at startup.
    cmd = build(framerate=60, action_repeat=4, speedup=8, show_window=False)
    assert all(" " not in arg for arg in cmd[1:])


def test_fixed_fps_is_split_into_two_tokens():
    cmd = build(framerate=60)
    assert "--fixed-fps" in cmd
    assert cmd[cmd.index("--fixed-fps") + 1] == "60"


def test_framerate_none_omits_the_flag():
    assert not any("fixed-fps" in arg for arg in build())


def test_plugin_arguments_keep_the_equals_form():
    cmd = build(port=11010, seed=3, action_repeat=4, speedup=8)
    assert "--port=11010" in cmd
    assert "--env_seed=3" in cmd
    assert "--action_repeat=4" in cmd
    assert "--speedup=8" in cmd


def test_hidden_window_adds_the_headless_flags():
    cmd = build(show_window=False)
    assert "--disable-render-loop" in cmd
    assert "--headless" in cmd


def test_extra_kwargs_are_forwarded():
    assert "--custom_arg=7" in build(custom_arg=7)


def test_env_path_stays_first():
    assert build()[0] == "game.x86_64"
