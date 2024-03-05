import numpy as np


def remove_large_objects(segments, maxsize):

    """Remove large segmented objects

    Parameters
    ----------
    segments: numpy array of segmentation labels
    maxsize: max pixel size

    Returns
    -------
    out : 2D label numpy array

    """

    out = np.copy(segments)
    component_sizes = np.bincount(segments.ravel())

    too_large = component_sizes > maxsize
    too_large_mask = too_large[segments]
    out[too_large_mask] = 0

    return out


def run(**kwargs):

    labels = kwargs.get('labels')
    maxsize = int(kwargs.get('maxsize'))

    cellpose_label = remove_large_objects(labels, maxsize)

    return {'labels': cellpose_label}
