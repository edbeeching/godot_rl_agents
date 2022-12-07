from distutils.core import setup
from setuptools import find_packages
# https://packaging.python.org/en/latest/tutorials/packaging-projects/
# https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/
__version__ = "0.3.0.a2"  # expected format is one of x.y.z.dev0, or x.y.z.rc1 or x.y.z (no to dashes, yes to dots)

REQUIRED_PKGS = [
    "numpy",
    "huggingface_hub>=0.10",  # For sharing objects, environments & trained RL policies
]


DEV_REQUIRE = []

TESTS_REQUIRE = [
    "pytest",
    "pytest-xdist",
]
SB3_REQUIRE = ["gym==0.21", "stable-baselines3"]
RLLIB_REQUIRE = ["ray[rllib]"]
SAMPLE_FACTORY_REQUIRE = ["sample-factory", "gym==0.26.2"]
QUALITY_REQUIRE = ["black[jupyter]~=22.0", "flake8>=3.8.3", "isort>=5.0.0", "pyyaml>=5.3.1"]

EXTRAS_REQUIRE = {
    "dev": DEV_REQUIRE + TESTS_REQUIRE + QUALITY_REQUIRE,
    "test": TESTS_REQUIRE,
    "sb3":SB3_REQUIRE,
    "rllib":RLLIB_REQUIRE,
    "sf":SAMPLE_FACTORY_REQUIRE,
}


setup(
    name="godot_rl",
    version=__version__,
    description="A Deep Reinforcement Learning package for the Godot game engine",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Edward Beeching.",
    author_email="edbeeching@gmail.com",
    url="https://github.com/edbeeching/godot_rl_agents",
    download_url="https://github.com/edbeeching/godot_rl_agents/tags",
    license="MIT",
    package_dir={"": "godot_rl"},
    packages=find_packages(where="godot_rl"),
    install_requires=REQUIRED_PKGS,
    extras_require=EXTRAS_REQUIRE,
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="godot simulation environments machine learning reinforcement learning deep learning video games",
    zip_safe=False,  # Required for mypy to find the py.typed file
    python_requires=">=3.8",

    entry_points={
    'console_scripts': [
        'gdrl = godot_rl.main:main',
    ]
    }
)