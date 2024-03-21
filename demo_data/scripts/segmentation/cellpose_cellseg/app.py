import numpy as np
import cv2
from cellpose import models
import re


def cellpose_cellseg(img, seg_channels, diameter, scaling):

    """Segment image by cellpose deeplearning method

    Parameters
    ----------
    img : Multichannel image as numpy array
    seg_channels: list of indices to use for nuclear segmentation
    diameter: typical size of nucleus
    scaling: Integer value scaling

    Returns
    -------
    labels_final : per cell segmentation as numpy array

    """
    temp2 = np.zeros((img.shape[1], img.shape[2]))
    for i in seg_channels:
        temp = img[i]
        temp2 = temp + temp2

    seg_image = temp2
    seg_image = cv2.resize(
        seg_image,
        (
            seg_image.shape[1] * scaling,
            seg_image.shape[0] * scaling
        ),
        interpolation=cv2.INTER_NEAREST,
    )

    # model = models.Cellpose(
    #     device=mxnet.cpu(),
    #     torch=False,
    #     gpu=False,
    #     model_type="nuclei"
    # )
    model = models.Cellpose(gpu=False, model_type="nuclei")

    labels, _, _, _ = model.eval(
        [seg_image[::1, ::1]],
        channels=[[0, 0]],
        diameter=diameter
    )

    labels2 = np.float32(labels[0])

    labels_final = cv2.resize(
        labels2,
        (
            labels2.shape[1] // scaling,
            labels2.shape[0] // scaling
        ),
        interpolation=cv2.INTER_NEAREST,
    )

    labels_final = np.uint32(labels_final)

    return labels_final


def run(**kwargs):

    image = kwargs.get('image')

    channel_list = kwargs.get("channel_list", [])
    channel_list = [re.sub("[^0-9a-zA-Z]", "", item).lower().replace("target", "") for item in channel_list]

    all_channels = kwargs.get("all_channels", [])
    channel_list: list[int] = [
        all_channels.index(channel)
        for channel in channel_list
        if channel in all_channels
    ]
    channel_list.sort()

    scaling = int(kwargs.get('scaling'))
    diameter = int(kwargs.get('diameter'))
    print(channel_list, diameter, scaling)

    cellpose_label = cellpose_cellseg(image, channel_list, diameter, scaling)

    return {'labels': cellpose_label}
