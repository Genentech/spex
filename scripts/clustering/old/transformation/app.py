import numpy as np


def run(**kwargs):

    df = kwargs.get('dataframe')
    # markers = kwargs.get('markers')

    data = df.to_numpy()
    _, col = df.shape
    markers = [i for i in range(col) if i not in [0, 1, 2]]

    data_for_calc = data[:, markers]

    data_for_calc = np.arcsinh(data_for_calc / 5)
    data[:, markers] = data_for_calc
    return {
        'transformed': data,
        'markers': markers
    }
