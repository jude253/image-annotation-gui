# Image Annotation GUI

[![PyPI - Version](https://img.shields.io/pypi/v/image-annotation-gui.svg)](https://pypi.org/project/image-annotation-gui)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/image-annotation-gui.svg)](https://pypi.org/project/image-annotation-gui)

-----

## Table of Contents

- [Overview](#Overview)
- [Dependencies](#Dependencies)
- [Installation](#installation)
- [Usage](#Usage)
- [License](#license)

## Overview

The goal of this repository is to make it very easy and scalable to add
annotations to images for training ML models.

#### Current State

At the moment, there is not way to adjust annotations once they are created.
However, it is possible to navigate away from an image, then navigate back
and create new annotations, which will overwrite the existing annotations.
The annotations that are written to disk are just dumps of the plotly
shapes json.  It also takes a while to load images and update the page.
I am not sure if there is something I can do to fix this, but showing
the user that the page is loading would be nice.  I imagine it will be
even slower with larger image files.

#### Future State

Ideally, there would be a way to update annotations from disk and from
currently drawn annotations as well as label them. Also, it would be
nice to be more systematic about the json storage, but at the moment it
is minimal, which also leaves nice flexiblity for the future.

## Dependencies

- Hatch: https://hatch.pypa.io/latest/

## Installation

```console
pip install image-annotation-gui
```

## Usage

1. Drag and drop images to annotate under `image_data/`
1. Run Command: `hatch run start`
1. Open web browser to page specified in terminal


## License

`image-annotation-gui` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
