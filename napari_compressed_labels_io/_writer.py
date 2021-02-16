"""
This module is an example of a barebones writer plugin for napari

It implements the ``napari_get_writer`` and ``napari_write_image`` hook specifications.
see: https://napari.org/docs/dev/plugins/hook_specifications.html

Replace code below according to your needs
"""

from napari_plugin_engine import napari_hook_implementation
import zarr
import os

@napari_hook_implementation(specname='napari_write_labels')
def labels_to_zarr(path, data, meta):
    """Write a 2D+ labels layer to zarr, chunked along the
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
    """
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
    """Given a 3D label layer and 3D stack of images, write corresponding
    image/label pairs to zarrs

    Parameters
    ----------
    path : str or list of str
        Path(s) to write layers
    layer_types : list of str
        List of layer types that will be provided to the writer function. This
        implementation supports image and label types
    """
    if isinstance(path, str):
        path = [path]
    
    if not all([pth.endswith('.zarr') for pth in path]):
        return None

    if not all([layer == 'image' or layer == 'labels' for layer in layer_types]):
        return None

    return write_label_image_pairs

def write_label_image_pairs(path, layer_data):
    """Write stack of labels and images into individual zarrs sorted into
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
    """
    layers = [layer[0] for layer in layer_data]
    shapes = [layer.shape for layer in layers]
    
    
    if not all([len(shape)==len(shapes[0]) for shape in shapes]):
        return None

    # check each shape is the same
    for i in range(len(shapes[0])):
        if not all([shpe[i] == shapes[0][i] for shpe in shapes]):
            return None
    
    layer_shape = shapes[0]
    n_pairs = layer_shape[0]
    im_shape = layer_shape[1:]


    images = [layer for layer in layer_data if layer[2]=='image']
    n_ims = len(images)

    labels = [layer for layer in layer_data if layer[2]=='labels']
    n_labels = len(labels)
    os.makedirs(path)

    # for each image/label on the stack
    for i in range(n_pairs):
        f_out = os.path.join(path, i)
        os.mkdir(f_out)

        for (im, meta, _) in images+labels:
            out_zarr = zarr.open(
                os.path.join(f_out, f"{meta['name']}_{i}"),
                mode='w',
                shape=im_shape
            )
            out_zarr[:] = im[:]


