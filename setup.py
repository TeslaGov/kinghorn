import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="kinghorn",
    version="0.0.7",
    description="Cache AWS resources",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/TeslaGov/kinghorn",
    author="Jon Crain",
    author_email="jwc9412@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["kinghorn"],
    include_package_data=True,
    install_requires=["boto3"],
)
