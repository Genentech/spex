from skimage.segmentation import expand_labels


def simulate_cell(labels, dist):

    """Dilate labels by fixed amount to simulate cells

    Parameters
    ----------
    labels: numpy array of segmentation labels
    dist: number of pixels to dilate

    Returns
    -------
    out : 2D label numpy array with simulated cells

    """

    return expand_labels(labels, dist)


def run(**kwargs):

    dist = int(kwargs.get('dist'))
    labels = kwargs.get('labels')
    expanded = simulate_cell(labels, dist)

    return {'labels': expanded}
