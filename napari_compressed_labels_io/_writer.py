'''
This module is an example of a barebones writer plugin for napari

It implements the ``napari_get_writer`` and ``napari_write_image`` hook specifications.
see: https://napari.org/docs/dev/plugins/hook_specifications.html

Replace code below according to your needs
'''

import json
from napari_plugin_engine import napari_hook_implementation
import zarr
import os

@napari_hook_implementation(specname='napari_write_labels')
def labels_to_zarr(path, data, meta):
    '''Write a 2D+ labels layer to zarr, chunked along the
    last two dimensions, presumed shape (..., y, x)

    Parameters
    ----------
    path : str or list of str
        Path or paths to save to disk. Each path must end with
        .zarr and this zarr cannot exist.
    data : array or list of array
        Labels data to be written
    meta : dict
        Labels metadata

    Returns
    -------
    str or list of lists or None
        Path(s) if any labels were written, otherwise None
    '''
    # TODO: should also handle lists of paths
    # TODO: check and/or write associated metadata
    if not path.endswith('.zarr'):
        return None

    zarr_shape = data.shape
    zarr_dtype = data.dtype

    # we assume x,y are the final two dimensions and chunk accordingly
    # TODO: is there a better way of checking dimensions?
    zarr_chunks = tuple([1 for i in range(len(zarr_shape) - 2)] + [1024, 1024])

    # TODO: compression type? Get from user?
    out_zarr = zarr.open(
        path, 
        mode='w',
        shape=zarr_shape,
        dtype=zarr_dtype,
        chunks=zarr_chunks
    )
    out_zarr[:] = data[:]
    return path


@napari_hook_implementation(specname='napari_get_writer')
def label_image_pairs_to_zarr(path, layer_types):
    '''Given a 3D label layer and 3D stack of images, write corresponding
    image/label pairs to zarrs

    Parameters
    ----------
    path : str or list of str
        Path(s) to write layers
    layer_types : list of str
        List of layer types that will be provided to the writer function. This
        implementation supports image and label types
    '''
    if isinstance(path, str):
        path = [path]
    
    if not all([pth.endswith('.zarr') for pth in path]):
        return None

    if not all([layer == 'image' or layer == 'labels' for layer in layer_types]):
        return None

    return write_label_image_pairs

def write_label_image_pairs(path, layer_data):
    '''Write stack of labels and images into individual zarrs sorted into
    corresponding label/image pairs

    Parameters
    ----------
    path : str
        path to save
    layer_data : List[Tuple[Any, Dict, str]]
        list of (data, meta, layer_type) to save

    Returns
    -------
    List[str]
        paths written to file
    '''
    shapes = [layer[0].shape for layer in layer_data]
    
    # check for same number of slices - assume first dimension
    if not all([shape[0] == shapes[0][0] for shape in shapes]):
        return None

    n_slices = shapes[0][0]
    os.makedirs(path)

    slice_zmeta = {}
    # for each image/label in the stack
    for i in range(n_slices):
        slice_fn = os.path.join(path, f"{i}")
        os.mkdir(slice_fn)
        slice_zmeta['meta'] = {'stack': 1} 
        slice_zmeta['data'] = {}

        for (im, meta, l_type) in layer_data:
            im_shape = im.shape[1:]
            layer_slice_fn = os.path.join(slice_fn, f"{meta['name']}")
            out_zarr = zarr.open(
                layer_slice_fn,
                mode='w',
                shape=im_shape,
                dtype=im.dtype
            )
            out_zarr[:] = im[i]

            # write individual layer slice zmeta
            layer_info = {
                'name': meta['name'],
                'shape': im.shape,
                'dtype': im.dtype.name,
            }
            if l_type == 'image' and meta['rgb']:
                layer_info['rgb']= 'true'

            layer_zmeta = {
                'meta' : {'stack': 0},
                'data': {}
            }
            layer_zmeta['data'][l_type] = [layer_info]

            with open(layer_slice_fn + '/.zmeta', 'w') as outfile:
                json.dump(layer_zmeta, outfile)

            if l_type in slice_zmeta['data']:
                slice_zmeta['data'][l_type].append(layer_info)
            else:
                slice_zmeta['data'][l_type] = [layer_info]
            
        with open(slice_fn + '/.zmeta', 'w') as outfile:
            json.dump(slice_zmeta, outfile)

    # write top level zmeta here at path
    slice_zmeta['meta']['stack'] = n_slices
    with open(path + '/.zmeta', 'w') as outfile:
            json.dump(slice_zmeta, outfile)
    return path
