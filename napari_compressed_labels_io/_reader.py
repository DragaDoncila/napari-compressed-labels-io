"""
This module is an example of a barebones numpy reader plugin for napari.

It implements the ``napari_get_reader`` hook specification, (to create
a reader plugin) but your plugin may choose to implement any of the hook
specifications offered by napari.
see: https://napari.org/docs/dev/plugins/hook_specifications.html

Replace code below accordingly.  For complete documentation see:
https://napari.org/docs/dev/plugins/for_plugin_developers.html
"""
import numpy as np
from napari_plugin_engine import napari_hook_implementation
import zarr

@napari_hook_implementation(specname='napari_get_reader')
def get_zarr_reader(path):
    """Read single zarr labels layers into napari

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """

    # if it's a list we don't deal with it yet
    if isinstance(path, list):
        return None

    # if we know we cannot read the file, we immediately return None.
    if not path.endswith(".zarr"):
        return None

    # otherwise we return the *function* that can read ``path``.
    return read_zarr_labels


def read_zarr_labels(path):
    """Take a path or list of paths and return a list of LayerData tuples.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of layer.
        Both "meta", and "layer_type" are optional. napari will default to
        layer_type=="image" if not provided
    """
    # load zarr
    data = zarr.open(path, mode='r')
    
    # optional kwargs for the corresponding viewer.add_* method
    add_kwargs = {}

    layer_type = "labels"  # optional, default is "image"
    return [(data, add_kwargs, layer_type)]
