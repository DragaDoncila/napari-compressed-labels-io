# napari-compressed-labels-io

[![License](https://img.shields.io/pypi/l/napari-compressed-labels-io.svg?color=green)](https://github.com/DragaDoncila/napari-compressed-labels-io/raw/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-compressed-labels-io.svg?color=green)](https://pypi.org/project/napari-compressed-labels-io)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-compressed-labels-io.svg?color=green)](https://python.org)
[![tests](https://github.com/DragaDoncila/napari-compressed-labels-io/workflows/tests/badge.svg)](https://github.com/DragaDoncila/napari-compressed-labels-io/actions)
[![codecov](https://codecov.io/gh/DragaDoncila/napari-compressed-labels-io/branch/master/graph/badge.svg)](https://codecov.io/gh/DragaDoncila/napari-compressed-labels-io)


## Description

This napari plugin provides a reader and writer for stacks of 3D images with associated labels.

The writer will save the images and labels in individual zarrs corresponding to each slice, making use of a .zmeta file whose specification is described below. The reader will then allow the loading of the entire stack of all layers, all layers of an individual slice or a single layer of an individual slice. The intent of this plugin is to provide a portable format for labels and their images while maintaining the flexiblity of opening parts of the stack as individual images.

## .zmeta

This metadata file contains information about the layer types in the stack and in each individual slice, as well as the number of image/label slices. This allows the reader plugin to load the correct layer types with appropriate names both at a stack level and at the individual slice level.

### An example .zmeta specification

```json
{
    "meta": {
        "stack": 7                               # number of slices in the entire stack (1 for an individual slice, 0 for a layer within a slice)
    },
    "data": {
        "image" : [                              # all image layers must be listed here
            {
                "name": "leaves_example_data",
                "shape": [790, 790, 3],
                "dtype": "uint8",
                "rgb": true                      # where rgb is false the image will be loaded as greyscale (colormap support has not yet been implemented)
            }
        ],
        "labels" : [
            {
                "name": "oak",
                "shape": [790, 790],
                "dtype": "int64"
            },
            {
                "name": "bg",
                "shape": [790, 790],
                "dtype": "int64"
            }
        ]
    }
}

```


----------------------------------

This [napari] plugin was generated with [Cookiecutter] using with [@napari]'s [cookiecutter-napari-plugin] template.

<!--
Don't miss the full getting started guide to set up your new package:
https://github.com/napari/cookiecutter-napari-plugin#getting-started

and review the napari docs for plugin developers:
https://napari.org/docs/plugins/index.html
-->

## Installation

You can install `napari-compressed-labels-io` via [pip]:

    pip install napari-compressed-labels-io

## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [MIT] license,
"napari-compressed-labels-io" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin
[file an issue]: https://github.com/DragaDoncila/napari-compressed-labels-io/issues
[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
