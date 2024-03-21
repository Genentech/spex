from skimage import segmentation


def run(**kwargs):

    expanded = kwargs.get('labels')

    contour = segmentation.find_boundaries(expanded, connectivity=1, mode='thick', background=0)

    return {'contour': contour}
