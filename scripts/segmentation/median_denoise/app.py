import re
import numpy as np
from skimage.filters import median
from skimage.morphology import disk
from skimage.util import apply_parallel


def median_denoise(image, kernel, ch):

    """Non local means denoising

    Parameters
    ----------
    image : Multichannel numpy array (C,X,Y)
    kernel: int, 5-7 is a typical range
    ch: list of int, indexes of channels to be denoised

    Returns
    -------
    Image Stack : Denoised image stack as numpy array (C,X,Y)

    """

    filter_channels = ch

    def median_denoise_wrap(array):
        correct = array[0]
        correct = median(correct, disk(kernel))
        return correct[np.newaxis, ...]

    denoise = apply_parallel(
        median_denoise_wrap,
        image,
        chunks=(1, image.shape[1], image.shape[2]),
        dtype="float",
        compute=True,
    )

    filtered = []

    for i in range(0, image.shape[0], 1):
        if i in filter_channels:
            temp = denoise[i]
            temp = np.expand_dims(temp, 0)
            if i == 0:
                filtered = temp
            else:
                filtered = np.concatenate((temp, filtered), axis=0)
        else:
            temp = image[i]
            temp = np.expand_dims(temp, 0)
            if i == 0:
                filtered = temp
            else:
                filtered = np.concatenate((temp, filtered), axis=0)

    f_denoise = np.flip(filtered, axis=0)

    return f_denoise


def run(**kwargs):

    image = kwargs.get("image")
    channel_list = kwargs.get("channel_list", [])
    channel_list = [re.sub("[^0-9a-zA-Z]", "", item).lower().replace("target", "") for item in channel_list]

    all_channels = kwargs.get("all_channels")
    channel_list: list[int] = [
        all_channels.index(channel)
        for channel in channel_list
        if channel in all_channels
    ]
    channel_list.sort()

    kernel = kwargs.get("kernel", 5)
    if isinstance(kernel, str):
        kernel = int(kernel)
    image = median_denoise(image, kernel, channel_list)

    return {"image": image}
