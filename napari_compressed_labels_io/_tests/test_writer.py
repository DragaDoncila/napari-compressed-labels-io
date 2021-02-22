from napari_compressed_labels_io import labels_to_zarr, label_image_pairs_to_zarr
import os 
import numpy as np


def test_labels_to_zarr_successful(tmp_path):
    out_pth = os.path.join(tmp_path, 'out_labels.zarr')
    data = np.random.randint(4, size=(3, 100, 100))
    meta = {
        'name': 'test_labels'
    }
    ret = labels_to_zarr(out_pth, data, meta)
    assert isinstance(ret, str), "Saving valid labels to zarr does not return path"
    assert os.path.exists(out_pth), "Saving valid data does not save a zarr to expected path"


def test_label_image_pair_to_zarr_successful(tmp_path):
    out_pth = os.path.join(tmp_path, 'out_stack.zarr')

    ret = label_image_pairs_to_zarr(out_pth, ['image', 'labels'])
    assert callable(ret), "Passing valid path and layer types does not return writer"
    
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
    ret_pth = ret(out_pth, [im_layer, labels_layer])
    
    assert isinstance(ret_pth, str), "Saving valid label image stack to zarr does not return path"
    assert os.path.exists(out_pth), "Saving valid label image stack does not save a zarr to expected path"