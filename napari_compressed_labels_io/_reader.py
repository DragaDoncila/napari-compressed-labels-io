"""
This module is an example of a barebones numpy reader plugin for napari.

It implements the ``napari_get_reader`` hook specification, (to create
a reader plugin) but your plugin may choose to implement any of the hook
specifications offered by napari.
see: https://napari.org/docs/dev/plugins/hook_specifications.html

Replace code below accordingly.  For complete documentation see:
https://napari.org/docs/dev/plugins/for_plugin_developers.html
"""
from napari_plugin_engine import napari_hook_implementation
import zarr
import os
from glob import glob
import dask.array as da

# @napari_hook_implementation(specname='napari_get_reader')
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

    # TODO: check that a .zarray file is at the top level inside the zarr to return quickly
    # if it's actually a paired zarr or ome-zarr


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


@napari_hook_implementation(specname='napari_get_reader')
def get_label_image_stack(path):
    if not path.endswith(".zarr"):
        return None

    dir_paths = glob(f'{path}/*')
    if not all([os.path.isdir(pth) and pth[-1].isnumeric() for pth in dir_paths]):
        return None

    for dir in dir_paths:
        content_paths = glob(f'{dir}/*')
        if not all([('image' in pth or 'labels' in pth) for pth in content_paths]):
            return None

    return read_label_image_stack

def read_label_image_stack(path):
    dirs = sorted(glob(f'{path}/*'))
    n_pairs = len(dirs)

    content_paths = sorted(glob(f'{dirs[0]}/*'))

    layers = [[] for _ in range(len(content_paths))]
    # TODO: delay this
    layer_shapes = [zarr.open(pth).shape for pth in content_paths]
    layer_names = ['_'.join(os.path.basename(pth).split('_')[:-2]) for pth in content_paths]
    layer_types = ['image' if 'image' in pth else 'labels' for pth in content_paths]

    for dir in dirs:
        layer_paths = sorted(glob(f'{dir}/*'))
        for i, pth in enumerate(layer_paths):
            layers[i].append(zarr.open(pth, mode='r'))
    
    stacked_layers = []
    for i, layer in enumerate(layers):
        stacked = da.stack(layer)
        add_kwargs = {
            'name': layer_names[i]
        }
        layer_type = layer_types[i]
        if layer_type == 'image':
            add_kwargs['rgb'] = True
            add_kwargs['contrast_limits'] = (0, 1)
        stacked_layers.append(
            (stacked, add_kwargs, layer_type)
        )

    return stacked_layers
