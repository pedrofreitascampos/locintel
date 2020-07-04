from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="traces",
    version="1.0",
    author="das-routing",
    author_email="https://autonomous-services.slack.com/messages/das-routing",
    setup_requires=["very-good-setuptools-git-version"],
    description="A library to support trace and probe data processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.mobilityservices.io/am/routing-python/traces",
    keywords="routing routes qa traces",
    packages=find_namespace_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests", "pydruid", "das-routing-core"],
    include_package_data=True,
)
