from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="geotools",
    version_format="0.9",
    setup_requires=["very-good-setuptools-git-version"],
    author="Pedro Campos",
    author_email="pedrofreitascampos@gmail.com",
    description="Core geo tools library for mapping and routing applications in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_namespace_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests", "numpy", "polyline", "geojson", "shapely", "utm"],
)
