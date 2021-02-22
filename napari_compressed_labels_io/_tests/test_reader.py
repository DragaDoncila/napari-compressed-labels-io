import numpy as np
import os

from numpy.testing._private.utils import assert_array_almost_equal
from napari_compressed_labels_io import get_zarr_labels, get_label_image_stack
from napari_compressed_labels_io._writer import labels_to_zarr, write_label_image_pairs


def test_get_zarr_labels_successful(tmp_path):
    out_pth = os.path.join(tmp_path, 'out_labels.zarr')
    data = np.random.randint(4, size=(3, 100, 100))
    meta = {
        'name': 'test_labels'
    }
    labels_to_zarr(out_pth, data, meta)

    reader = get_zarr_labels(out_pth)
    assert callable(reader), "Get reader does not return reader given valid path"

    layer_data = reader(out_pth)
    assert_array_almost_equal(data, layer_data[0][0]), "Reader did not return same data"
    assert layer_data[0][2] == 'labels', "Reader did not return labels layer"

def test_get_label_image_stack_successful(tmp_path):
    out_pth = os.path.join(tmp_path, 'out_stack.zarr')
    label_data = np.random.randint(4, size=(3, 100, 100))
    label_meta = {
        'name': 'test_labels'
    }
    labels_layer = (label_data, label_meta, 'labels')

    im_data = np.random.random((3, 100, 100))
    im_meta = {
        'name': 'test_im',
        'rgb': False
    }
    im_layer = (im_data, im_meta, 'image')
    ret_pth = write_label_image_pairs(out_pth, [labels_layer, im_layer])

    reader = get_label_image_stack(ret_pth)
    assert callable(reader), "Get reader does not return reader given valid image label stack"
    
    layers = reader(ret_pth)
    layer_types = [layer[2] for layer in layers]
    layer_names = [layer[1]['name'] for layer in layers]
    layer_data = [layer[0] for layer in layers]

    assert sorted(layer_types) == ['image', 'labels'], "Reader does not load correct layer types"
    assert sorted(layer_names) == ['test_im', 'test_labels'], "Reader does not preserve layer names"
    assert layer_data[0].shape == im_data.shape, "Reader does not stack layers correctly"