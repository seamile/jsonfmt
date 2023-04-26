#!/usr/bin/env python3
import setuptools
from jsonfmt import __version__

with open("README.md", "r") as f_readme:
    long_description = f_readme.read()

setuptools.setup(
    name="jsonfmt",
    version=__version__,
    python_requires=">=3.5",
    author="Seamile",
    author_email="lanhuermao@gmail.com",
    description="A JSON object formatting tool.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seamile/jsonfmt",
    entry_points={
        'console_scripts': ['jsonfmt=jsonfmt:main'],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities"
    ],
)
