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
        detector = PixelChangeFD(
            video=video,
            outlier_change_threshold=settings.get(
                'outlier_change_threshold', .5
            ),
            flag_outliers_buffer=settings.get('flag_outliers_buffer', 5),
            movement_threshold=settings.get('movement_threshold', .1),
            freezing_buffer=settings.get('freezing_buffer', 5),
            blur_ksize=settings.get('blur_ksize', 3),
        )
        detector.run()
        visualizer = Interface(detector=detector)
        visualizer.display()
        detector.save_meta()
        meta_analyzer = IntervalAggregatorMA(
            detector=detector,
            intervals=settings['intervals'],
            aggregation=lambda x: 1 - np.mean(x),
            include_start=settings.get('include_start', 1),
            include_end=settings.get('include_end', 1),
        )
        meta_analyzer.run()


if __name__ == '__main__':
    main()
