from aicsimageio import AICSImage
from aicsimageio.readers import BioformatsReader

from tifffile import TiffFile
import json
import re


def load_tiff(img, is_mibi=True):

    """Load image and check/correct for dimension ordering

    Parameters
    ----------
    img : Path of Multichannel tiff file
    is_mibi : Boolean. Does this image come from MIBI?

    Returns
    -------
    Image Stack : 2D numpy array
    Channels : list

    """
    file = img
    img = AICSImage(img, reader=BioformatsReader)

    # It is assumed that the dimension with largest length has the channels
    # channel_len = max(img.size("STCZ")) old
    dask_data = img.get_image_dask_data("STCZ")
    dim = dask_data.shape
    channel_len = max(dim)
    order = ["S", "T", "C", "Z"]

    def replace(channels: list):
        return [re.sub("[^0-9a-zA-Z]", "", item).lower().replace("target", "") for item in channels]

    x = 0
    for x in range(len(order)):
        if dim[x] == channel_len:
            break

    orientation = f'{order[x]}YX'
    args = {'T': 0, 'C': 0, 'Z': 0}
    if orientation == "TYX":
        args = {'S': 0, 'C': 0, 'Z': 0}
    if orientation == "CYX":
        args = {'S': 0, 'T': 0, 'Z': 0}
    if orientation == "ZYX":
        args = {'S': 0, 'T': 0, 'C': 0}

    image_true = img.get_image_dask_data(orientation, **args).compute()

    channel_list = replace(img.channel_names)
    if channel_list == ['0'] or channel_list == ['channel00']:
        channel_list = []
        with TiffFile(file) as tif:
            for page in tif.pages:
                description = json.loads(page.tags["ImageDescription"].value)
                channel_list.append(description["channel.target"])

        channel_list = replace(channel_list)

    return image_true, channel_list


def run(**kwargs):

    image = kwargs.get('image_path')
    image, channel_list = load_tiff(image)

    return {'image': image, 'all_channels': channel_list}
