"""
This module provides a reader for image stacks and their corresponding labels in zarr 
format.
"""

import json
from napari_plugin_engine import napari_hook_implementation
import zarr
import os
from glob import glob
import dask.array as da
import numpy as np

@napari_hook_implementation(specname='napari_get_reader')
def get_zarr_labels(path):
    """Read a single labels layer from zarr into napari

    Parameters
    ----------
    path : str or list of str
        path(s) to try reading

    Returns
    -------
    callable or None
        callable if path is a zarr file with a .zarray at the top level, otherwise None
    """
    if isinstance(path, str):
        path = [path]
    
    # all paths must end with zarr
    if not all(pth.endswith('.zarr') for pth in path):
        return None
    
    # all paths must have a .zarray file at the top level
    if not all(os.path.isfile(os.path.join(pth, '.zarray')) for pth in path):
        return None

    return read_zarr_labels

def read_zarr_labels(path):
    """Read a single stack of zarr labels into napari

    Parameters
    ----------
    path : str or list of str
        path to read labels from

    Returns
    -------
    list of tuples (data, meta, layer_type)
       layers read from path 
    """
    data = zarr.open(path, mode='r')

    add_kwargs = {}

    layer_type = 'labels'

    return [(data, add_kwargs, layer_type)]

@napari_hook_implementation(specname='napari_get_reader')
def get_label_image_stack(path):
    """Returns a reader for a stack of corresponding image and label slices.
    
    Checks for the existence of .zmeta file at path and returns reader if this exists,
    otherwise None.

    Parameters
    ----------
    path : str or list of str
        path to try reading

    Returns
    -------
    callable or None
        reader for layers if path can be read, otherwise None
    """
    if isinstance(path, str):
        path = [path]

    # a .zmeta file MUST be present for this stack to be read
    for pth in path:
        if not os.path.isfile(os.path.join(pth, '.zmeta')):
            return None

    return read_label_image_stack

def read_label_image_stack(path):
    """Returns stacked images and labels layers from the given path using
    .zmeta file

    Parameters
    ----------
    path : str
        path to label and/or image stacks

    Returns
    -------
    list of tuples (data, meta, layer_type)
       layers read from path 
    """
    with open(os.path.join(path, '.zmeta'), "r") as f:
        meta = json.load(f)
        
        all_layers = []
        if 'image' in meta['data']:
            ims = read_layers(path, meta, 'image')
            all_layers.extend(ims)
        if 'labels' in meta['data']:
            labels = read_layers(path, meta, 'labels')
            all_layers.extend(labels)

        return all_layers

def read_layers(path, meta, l_type):
    npairs = meta['meta']['stack']

    layer_meta = meta['data'][l_type]
    layer_names = [im['name'] for im in layer_meta]

    layers = [[] for _ in range(len(layer_meta))]
    for i, name in enumerate(layer_names):
        if npairs == 0:
            layer_data = zarr.open(
                path,
                mode='r'
            )
            layers[i].append(layer_data)
        else:
            for j in range(npairs):
                slice_path = get_slice_path(path, name, j, npairs)
                layer_data = zarr.open(
                    slice_path,
                    mode='r'
                )
                layers[i].append(layer_data)

    stacked_layers = []
    for i, layer in enumerate(layers):
        stacked = da.stack(layer)
        add_kwargs = {
            'name': layer_names[i]
        }
        if 'rgb' in layer_meta[i]:
            add_kwargs['rgb'] = True
        stacked_layers.append(
            (stacked, add_kwargs, l_type)
        )

    return stacked_layers

def get_slice_path(root, layer_name, current_pair, n):
    # we're at slice level, simply join root with layer name
    if n == 1:
        return os.path.join(root, layer_name)
    
    # we're at stack level, need to join with current_pair to get the appropriate slice
    return os.path.join(os.path.join(root, str(current_pair)), layer_name)