from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="das-routing-quality",
    version="1.0",
    author="das-routing",
    author_email="https://autonomous-services.slack.com/messages/das-routing",
    setup_requires=["very-good-setuptools-git-version"],
    description="A library supporting route quality analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.mobilityservices.io/am/routing-python/quality",
    keywords="routing routes qa",
    packages=find_namespace_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
    ],
    install_requires=["shapely", "dtw", "pymongo", "matplotlib", "das-routing-core"],
    include_package_data=True,
)
