import numpy as np

from movement_detector import (
    CvVideo,
    Interface,
    PixelChangeFD,
)
from movement_detector.analysis import IntervalAggregatorMA
from movement_detector.utils import get_video_paths, get_project_path


def parse_settings():
    root = get_project_path()
    settings_path = root / 'settings.txt'
    settings = {}

    with open(settings_path) as f:
        for line in f:
            key, value = line.split(' = ')
            try:
                value = eval(value)
            except NameError:
                pass
            settings[key] = value

    return settings


def main():
    settings = parse_settings()

    vid_paths = get_video_paths()
    for video_path in vid_paths:
        video = CvVideo(file_path=video_path)
        meta_analyzer = IntervalAggregatorMA(
            vid_path=video_path,
            intervals=settings['intervals'],
            aggregation=lambda x: 1 - np.mean(x)
        )
        detector = PixelChangeFD(
            video=video,
            meta_analyzer=meta_analyzer,
            outlier_change_threshold=settings.get(
                'outlier_change_threshold', .2
            ),
            flag_outliers_buffer=settings.get('flag_outliers_buffer', 5),
            movement_threshold=settings.get('movement_threshold', .1),
            freezing_buffer=settings.get('freezing_buffer', 3),
            blur_ksize=settings.get('blur_ksize', 3),
        )
        detector.run()
        visualizer = Interface(detector=detector)
        visualizer.display()


if __name__ == '__main__':
    main()
