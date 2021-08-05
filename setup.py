import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="godot_rl_agents",
    version="0.0.1",
    author="Edward Beeching",
    author_email="edbeeching@gmail.com",
    description="A Deep Reinforcement Learning package for the Godot game engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/edbeeching/godot_rl_agents",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/edbeeching/godot_rl_agents/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # packages=setuptools.find_packages(where="godot_rl_agents"),
    packages=[
        "godot_rl_agents",
        "godot_rl_agents.core",
        "godot_rl_agents.tests",
    ],
    python_requires=">=3.6",
)
