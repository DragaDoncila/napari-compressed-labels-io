try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from ._reader import get_zarr_reader
from ._writer import labels_to_zarr, label_image_pairs_to_zarr


