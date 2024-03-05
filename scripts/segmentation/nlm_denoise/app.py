import numpy as np
from skimage.restoration import denoise_nl_means, estimate_sigma
from skimage.util import apply_parallel


def nlm_denoise(image, patch, dist):

    """Non local means denoising

    Parameters
    ----------
    image : Multichannel numpy array (C,X,Y)
    patch: int, Patch size (5 is typical)
    dist: int, ignore pixels above this threshold (6 is typical)

    Returns
    -------
    Image Stack : Denoised image stack as numpy array (C,X,Y)

    """

    def nlm_denoise_wrap(array):
        correct = array[0]
        sigma_est = np.mean(estimate_sigma(correct, multichannel=False))
        correct = denoise_nl_means(
            correct,
            h=0.6 * sigma_est,
            sigma=sigma_est,
            fast_mode=True,
            patch_size=patch,
            patch_distance=dist,
            multichannel=False,
            preserve_range=True,
        )
        return correct[np.newaxis, ...]

    denoise = apply_parallel(
        nlm_denoise_wrap,
        image,
        chunks=(1, image.shape[1], image.shape[2]),
        dtype="float",
        compute=True,
    )

    return denoise


def run(**kwargs):

    image = kwargs.get('image')
    patch = kwargs.get('patch') or 5
    dist = kwargs.get('dist') or 6
    image = nlm_denoise(image, patch, dist)

    return {'image': image}
