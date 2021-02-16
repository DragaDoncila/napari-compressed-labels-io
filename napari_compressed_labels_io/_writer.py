"""
This module is an example of a barebones writer plugin for napari

It implements the ``napari_get_writer`` and ``napari_write_image`` hook specifications.
see: https://napari.org/docs/dev/plugins/hook_specifications.html

Replace code below according to your needs
"""

from napari_plugin_engine import napari_hook_implementation
import zarr

@napari_hook_implementation
def napari_write_labels(path, data, meta):
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
    

