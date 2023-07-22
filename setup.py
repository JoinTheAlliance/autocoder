import os
from setuptools import setup

project_name = "autocoder"
version="0.0.1"

long_description = ""
with open("README.md", "r") as fh:
    long_description = fh.read()
    # search for any lines that contain <img and remove them
    long_description = long_description.split("\n")
    long_description = [line for line in long_description if not "<img" in line]
    # now join all the lines back together
    long_description = "\n".join(long_description)

# read requirements.txt to an array
with open("requirements.txt") as f:
    requirements = f.read().strip().splitlines()

setup(
    name=project_name,
    version=version,
    description="Code that basically writes itself",
    long_description=long_description,  # added this line
    long_description_content_type="text/markdown",  # and this line
    url="https://github.com/AutonomousResearchGroup/autocoder",
    author="Moon",
    author_email="shawmakesmagic@gmail.com",
    license="MIT",
    packages=[project_name],
    install_requires=requirements,
    readme="README.md",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
