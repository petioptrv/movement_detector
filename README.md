# Movement Detector

INSTALLATION

1. Install Python 3 for your operating system. (https://www.python.org/downloads/)
2. Open a Terminal in MacOS or a Command Prompt in Windows.
3. Type "cd " (with the space at the end) and drag and drop the movement_detector folder onto the window. 
    Hit Enter.
4. Type "python setup.py install"

SETTINGS (settings.txt)

1. freezing_window — How many consecutive frames must register lack of movement to be set as "freezing".
2. interval_start_times — The start times of each interval in seconds measured from the start of the video.
3. outlier_change_threshold — How many standard deviations away from the mean movement detected must a 
    frame be to be flagged as an outlier (useful for handling flashing-light cueues).
4. flag_outliers_window — The majority in x consecutive frames must be outliers for those x frames to be
    flagged for user-review (e.g. if set to 5, 3 frames out of a set of 5 consecutive ones must be outliers in order to
    flag all 5 for user-review; set to 1 to make sure that every outlier is flagged)

DEMO

1. Copy the experiment videos in the "videos" folder.
    1.1 Videos can be arranged in a folder structure.
    1.2 All videos analyzed at the same time must have the same interval start and end times.
2. Open a Terminal in MacOS or a Command Prompt in Windows.
3. Type "cd " (with the space at the end) and drag and drop the movement_detector folder onto the window. 
    Hit Enter.
4. Type "python demo_visual.py" and hit Enter.
5. The videos will appear in randomized order to preserve condition blindness.
6. Basic controls (available before the video is fully analyzed and all data is loaded).
    6.1 Right arrow — Next frame.
    6.2 Left arrow — Previous frame.
    6.3 m — Set frame to "moving" and move to next frame.
    6.4 f — Set frame to "freezing" and move to next frame.
    6.5 N — Switch to next video in queue.
    6.6. P — Switch to previous video in queue.
7. Advanced controls (available only once the video is fully analyzed and all data is loaded).
    7.1 n — Jump to the next set of flagged outlier-frames.
    7.2 p — Jump to the previous set of flagged outlier-frames
    7.3 Escape — Exit manual video-analysis and output the results (only available once all videos analyzed).
8. The output csv is stored in the "results" folder.
