from skimage.measure import regionprops_table, regionprops
from skimage import measure
from anndata import AnnData
from vitessce.data_utils import to_uint8, optimize_adata
import pandas as pd
import numpy as np
import re


def parse_channel_list(channel_list, all_channels):

    new_all_channels = []
    for item in all_channels:
        if isinstance(item, str):
            item = re.sub("[^0-9a-zA-Z]", "", item).lower().replace("target", "")
        new_all_channels.append(item)

    new_channel_list = []
    for item in channel_list:
        if isinstance(item, str):
            item = re.sub("[^0-9a-zA-Z]", "", item).lower().replace("target", "")
        new_channel_list.append(item)

    channel_list_int = [
        new_all_channels.index(new_channel_list)
        for channel in channel_list
        if channel in all_channels
    ]
    if not channel_list_int:
        channel_list_int = new_channel_list

    return channel_list_int, all_channels


def feature_extraction(img, labels, channel_list, all_channels):
    """Extract per cell expression for all channels neeed delete later

    Parameters
    ----------
    img : Multichannel image as numpy array
    labels: 2d segmentation label numpy array
    channel_list: list containing channel index
    all_channels: list of all available channels

    Returns
    -------
    perCellDataDF : Pandas dataframe with cell by expression data

    """

    # Image=img
    # img = AICSImage(Image)

    # G et coords from labels and create a dataframe to populate mean intensities
    props = regionprops_table(labels, properties=["label", "centroid"])
    per_cell_data_df = pd.DataFrame(props)

    # Loop through each tiff channel and append mean intensity to dataframe
    for x in channel_list:

        try:
            image = img[x, :, :]

            props = regionprops_table(
                labels,
                intensity_image=image,
                properties=["mean_intensity"]
            )
            data_temp = pd.DataFrame(props)
            data_temp.columns = [all_channels[x]]
            per_cell_data_df = pd.concat([per_cell_data_df, data_temp], axis=1)
        except IndexError:
            print("oops")

    # export and save a .csv file
    # perCellDataDF.to_csv(image+'perCellDataCSV.csv')
    # perCellDataCSV=perCellDataDF.to_csv

    return per_cell_data_df


def feature_extraction_adata(img, labels, all_channels):
    """Extract per cell expression for all channels

    Returns
    -------
    perCellanndata: anndata single-cell object with all data
    :param labels:
    :param img: Multichannel image as numpy array
    :param all_channels:

    """

    label_array = labels

    props = measure.regionprops_table(label_array, intensity_image=np.transpose(img, (1, 2, 0)),
                                      properties=['label', 'area', 'centroid', 'mean_intensity'])
    perCellData = pd.DataFrame(props)

    perCellData.columns = ['cell_id', 'area_pixels', 'Y', 'X'] + all_channels  # rename columns

    coordinates = np.array([k for k in perCellData[['X', 'Y']].values.tolist()])

    props = regionprops(label_array)
    ordered_contours = []
    for region in props:
        # Find contours of the region
        contours = measure.find_contours(label_array == region.label, 0.5)

        if len(contours) > 0:
            # Select the contour with the largest area
            contour = max(contours, key=lambda contour: contour.shape[0])
        else:
            contour = contours[0]

        centroid = np.mean(contour, axis=0)

        # Calculate angles of the points with respect to the centroid
        angles = np.arctan2(contour[:, 0] - centroid[0], contour[:, 1] - centroid[1])

        # Sort points based on angles
        sorted_indices = np.argsort(angles)
        sorted_contour = contour[sorted_indices]

        ordered_contours.append(sorted_contour)

    adata = AnnData(perCellData[all_channels], obsm={"spatial": coordinates}, dtype="float32")
    adata.obsm['cell_polygon'] = np.array(ordered_contours, dtype=object)

    adata.obs['Cell_ID'] = perCellData[['cell_id']].values
    adata.obs['Nucleus_area'] = perCellData[['area_pixels']].values
    adata.obs['x_coordinate'] = perCellData[['X']].values
    adata.obs['y_coordinate'] = perCellData[['Y']].values

    adata.layers['X_uint8'] = to_uint8(adata.X, norm_along="global")  # vitessce only supports 8bit expression
    return adata


def run(**kwargs):
    image = kwargs.get('image')
    labels = kwargs.get('labels')

    channel_list, all_channels = parse_channel_list(kwargs.get("channel_list", []), kwargs.get("all_channels", []))
    if not channel_list:
        channel_list = list(range(len(all_channels)))

    adata = feature_extraction_adata(image, labels, all_channels)

    # deprecated
    df = feature_extraction(image, labels, channel_list, all_channels)
    # deprecated

    return {
        'adata': adata,
        'dataframe': df,
        'channel_list': channel_list,
        'all_channels': all_channels
    }
