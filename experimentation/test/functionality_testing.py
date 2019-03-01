from math import sqrt

import pandas as pd
import numpy as np

from src.video.video import CvVideo
from src.common.numpy_fns import get_dtype


def main():
    vid = CvVideo('/Users/petioptrv/Documents/Programming/Python/movement_detector/videos/demo_video.mp4')
    meta_data = pd.DataFrame(
        columns=['mean_diff', 'outlier', 'ref_frame', 'delta', 'flagged'],
        index=range(len(vid))
    )
    mean_frame = vid.mean()
    i = 0
    for frame in vid:
        meta_data.loc[i, 'mean_diff'] = np.mean(mean_frame - frame)
        i += 1
    meta_data.loc[:, 'mean_diff'] = meta_data['mean_diff'].astype(np.int16)  # enough for -255
    std2 = sqrt((meta_data['mean_diff'] * meta_data['mean_diff']).sum() / len(vid)) * 2
    meta_data.loc[:, 'outlier'] = meta_data['mean_diff'].abs() > std2
    non_outlier = ~meta_data['outlier']
    min_type = get_dtype(len(vid))
    ref_frame_idx = meta_data.index.to_series().where(non_outlier, np.nan).shift().astype(min_type)
    ref_frame_idx.iloc[0] = 0
    meta_data.loc[:, 'ref_frame'] = ref_frame_idx.ffill()
    pass


if __name__ == '__main__':
    main()
