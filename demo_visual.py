import os
from random import shuffle
from queue import Queue
import time

import cv2
import pandas as pd

from movement_detector.video import CvVideo
from movement_detector.detectors import PixelChangeDetector
from movement_detector.resource_manager import ResourceManager
from movement_detector.settings import PixelChangeSettings


def main():
    project_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_path)
    settings_txt_path = os.path.join(project_path, 'settings.txt')
    settings = PixelChangeSettings()
    with open(settings_txt_path) as f:
        for line in f:
            if line[-1:] == '\n':
                line = line[:-1]
            args = line.split(' ')
            if len(args) == 2:
                if args[0] == 'sensitivity':
                    args[0] = 'blur_ksize'
                settings.set_setting(args[0], int(args[1]))
            else:
                settings.set_setting(args[0], [int(arg) for arg in args[1:]])
    videos_path = os.path.join(project_path, 'videos')
    videos_file_structure = os.walk(videos_path)
    video_paths = []
    for folder in videos_file_structure:
        folder_path = folder[0]
        for file_name in folder[2]:
            if file_name[-4:] in ['.mp4', '.wmv']:
                video_paths.append(os.path.join(folder_path, file_name))
    shuffle(video_paths)
    analyzers = []
    job_queue = Queue()
    resource_manager = ResourceManager(job_queue=job_queue)
    resource_manager.start()
    for video_path in video_paths:
        analyzer = PixelChangeDetector(CvVideo(video_path), settings)
        analyzers.append((video_path, analyzer))
        job_queue.put((analyzer.run, (), {'timit': True}))
    job_queue.put((ResourceManager.stop, (), None))
    a_idx = 0
    switch = False
    while a_idx != len(analyzers):
        if switch:
            switch = False
        vid_path = analyzers[a_idx][0]
        analyzer = analyzers[a_idx][1]
        vid = CvVideo(vid_path)
        ms_per_frame = int(1 / vid.frame_rate * 1000) - 50
        play_video = False
        frame_sleep = ms_per_frame

        # interactive visualisation
        i = 0
        while not switch:
            # print frame
            frame_ = vid[i]
            meta_data = analyzer.meta(i)
            if pd.isna(meta_data['freezing']):
                colour = (0, 0, 255)
                status_text = 'Loading info'
            elif meta_data['freezing']:
                colour = (0, 0, 255)
                status_text = 'Freezing'
            else:
                colour = (0, 255, 0)
                status_text = 'Moving'
            cv2.putText(frame_, status_text, (10, 20), cv2.FONT_HERSHEY_COMPLEX, .5, colour, 2)
            outlier_text = ''
            if pd.isna(meta_data['outlier']):
                colour = (0, 0, 255)
                outlier_text = 'Loading info'
            elif meta_data['user_verified']:
                colour = (0, 255, 0)
                outlier_text = 'User-verified'
            elif meta_data['flagged']:
                colour = (0, 0, 255)
                outlier_text = 'Flagged'
            cv2.putText(frame_, outlier_text, (10, 40), cv2.FONT_HERSHEY_COMPLEX, .5, colour, 2)
            cv2.imshow('Video {} - Frame {}'.format(a_idx+1, i+1), frame_)

            # wait for user command
            if not play_video:
                key = cv2.waitKey(0)
                if key == 2:  # left
                    if i != 0:
                        i -= 1
                elif key == 3:  # right
                    if i != len(vid) - 1:
                        i += 1
                elif key == ord('f'):
                    analyzer.set_freezing(i)
                    if i != len(vid) - 1:
                        i += 1
                elif key == ord('m'):
                    analyzer.set_moving(i)
                    if i != len(vid) - 1:
                        i += 1
                elif key == ord('n'):
                    search_started = False
                    while True:
                        if i == len(vid) - 1:
                            break
                        meta_data = analyzer.meta(i)
                        if pd.isna(meta_data['flagged']):
                            break
                        if meta_data['flagged']:
                            if search_started:
                                break
                        else:
                            search_started = True
                        i += 1
                elif key == ord('p'):
                    search_started = False
                    while True:
                        if i == 0:
                            break
                        meta_data = analyzer.meta(i)
                        if pd.isna(meta_data['flagged']):
                            break
                        if meta_data['flagged']:
                            if search_started:
                                break
                        else:
                            search_started = True
                        i -= 1
                elif key == ord(' '):
                    play_video = True
                elif key == ord('N'):
                    if a_idx != len(analyzers) - 1:
                        a_idx += 1
                        switch = True
                elif key == ord('P'):
                    if a_idx != 0:
                        a_idx -= 1
                        switch = True
                elif key == 27:  # escape
                    all_analyzed = True
                    for _, _analyzer in analyzers:
                        if not _analyzer.analysis_performed():
                            all_analyzed = False
                            break
                    if all_analyzed:
                        a_idx = len(analyzers)
                        switch = True
            else:
                key = cv2.waitKey(frame_sleep) & 0xFF
                if key != 255:  # space
                    play_video = False
                else:
                    i += 1
            cv2.destroyAllWindows()
    cv2.destroyAllWindows()
    while True:
        done = True
        for _, analyzer in analyzers:
            if not analyzer.analysis_performed():
                done = False
        if done:
            break
        else:
            time.sleep(5)
    start_times = settings.get_value('interval_start_times')
    results = pd.DataFrame(columns=['Interval {}'.format(i) for i in range(len(start_times))])
    for video_path, analyzer in analyzers:
        video_path_idx = video_path[len(videos_path)+1:]
        results.loc[video_path_idx] = analyzer.get_freezing_percentages()
    results_path = os.path.join(project_path, 'output', 'results.csv')
    results = results.sort_index()
    results.to_csv(results_path)


if __name__ == '__main__':
    main()
