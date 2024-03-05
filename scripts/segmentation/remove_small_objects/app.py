import numpy as np


def remove_small_objects(segments, minsize):

    """Remove small segmented objects

    Parameters
    ----------
    segments: numpy array of segmentation labels
    minsize: minimum pixel size

    Returns
    -------
    out : 2D label numpy array

    """

    out = np.copy(segments)
    component_sizes = np.bincount(segments.ravel())

    too_small = component_sizes < minsize
    too_small_mask = too_small[segments]
    out[too_small_mask] = 0

    return out


def run(**kwargs):

    new_label = kwargs.get('labels')
    minsize = int(kwargs.get('minsize'))

    cellpose_label = remove_small_objects(new_label, minsize)

    return {'new_label': cellpose_label}
