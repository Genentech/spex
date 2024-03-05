from aicsimageio import AICSImage
from aicsimageio.writers import OmeTiffWriter, OmeZarrWriter
from tifffile import imread, imsave, TiffWriter, imwrite, TiffFile
import json

import re


def convert_mibitiff2zarr(inputpath, outputpath):
    """convert mibi tiff to zarr

    Parameters
    ----------
    inputpath : Path of tiff file
    outputpath : Path of ometiff or omezarr file. Note: for omezarr, the path must end in *.zarr/0

    """
    img = AICSImage(inputpath)
    im_array = img.get_image_data("ZYX", T=0, C=0)

    Channel_list = []
    with TiffFile(inputpath) as tif:
        for page in tif.pages:
            # get tags as json
            description = json.loads(page.tags['ImageDescription'].value)
            Channel_list.append(description['channel.target'])

    writer = OmeZarrWriter(output)
    writer.write_image(im_array, image_name="Image:0", dimension_order="CYX", channel_names=Channel_list,
                       scale_num_levels=4, physical_pixel_sizes=None, channel_colors=None)

    print('conversion complete')


def load_image(imgpath):
    """Load image and check/correct for dimension ordering

    Parameters
    ----------
    img : Path of ometiff or omezarr file. Note: for omezarr, the path must end in *.zarr/0

    Returns
    -------
    Image Stack : 2D numpy array
    Channels : list

    """

    img = AICSImage(imgpath)

    dims = ['T', 'C', 'Z']
    shape = list(img.shape)
    channel_dim = dims[shape.index(max(shape[0:3]))]

    array = img.get_image_data(channel_dim + "YX")

    channel_list = img.channel_names

    if len(channel_list) != array.shape[0]:
        channel_list = []
        with TiffFile(imgpath) as tif:
            for page in tif.pages:
                # get tags as json
                description = json.loads(page.tags['ImageDescription'].value)
                channel_list.append(description['channel.target'])

    return array, channel_list


def run(**kwargs):
    image = kwargs.get('image_path')
    image, channel_list = load_image(image)

    return {'image': image, 'all_channels': channel_list}
