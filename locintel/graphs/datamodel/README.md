# Just a Utility for Recording Basemap Efficiently

## Why should we have a specification

The goal of this format specification is to have a convinient and unified way to store HD or SD map. It should be usable by all applications and thus easily be converted to any format and generated from any map provider.

## The library

A map is by essence a graph. We decide to store our map in a data format that is efficient and meaningful. That is the reason why we decided to use a standard graph library: *NetworkX*.

*NetworkX* is the main python library for graphs and has all the features required for an efficient graph handling and is used by plenty of external libraries. The documentation of *NetworkX* is available [here](https://networkx.github.io/documentation/stable/index.html).

Graphs shall be saved in the python pickle to a *.jurbey* file to be easily recognizable by everyone. It can be easily exported to this format thanks to [this](https://networkx.github.io/documentation/stable/reference/readwrite/generated/networkx.readwrite.gpickle.write_gpickle.html#networkx.readwrite.gpickle.write_gpickle) function.

The *.jurbey* file also provides some extra metadata:
- Version number
- Provider
- Region code

## The graph

In the map, we chose to represent road segments and connections as arcs (directed links). Arcs are connected by nodes which represent a point in space.

Here follows a real life example of how an intersection should be interpreted:

![Basic example](img/holsteinische.png "Basic example of a double way / one way intersection")
