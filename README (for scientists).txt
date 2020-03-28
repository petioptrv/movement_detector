# Movement Detector

INSTALLATION (MAC)

1. Install Python 3 for your operating system. (https://www.python.org/downloads/)
2. Open a Terminal window.
3. Type "chmod 700 path/to/file/run" where the part following "chmod 700" is the path to the file called "run". 
4. Hit Enter.

RUN

1. Copy the experiment videos in the "videos" folder.
    1.1 Videos can be arranged in a folder structure.
    1.2 All videos analyzed at the same time must have the same interval start and end times.
2. Open a Terminal window.
3. Drag and drop the file called "run" onto the terminal window.
4. Hit Enter.
5. Results will be in the "analysis" folder.

SETTINGS (settings.txt)

1. intervals - A list of the intervals' delimiting time-stamps. The start and end of the video are automatically
               included. E.g. for intervals 0-15, 15-30, and 30-45 seconds, where the video's duration is 45s, set
               equal to [15, 30].
2. outlier_change_threshold — The number of standard deviations from the mean that the pixel-change ratio must be
                              to be considered an outlier. Outlier frames are flagged for manual review.
3. flag_outliers_buffer — The number of consecutive frames that must be identified as outliers in order to flag
                          all those frames for review.
4. movement_threshold — A value between 0 and 1. The ratio of pixel-change areas relative to the area of the image
                        above which the frame will be flagged as containing movement.
5. freezing_buffer - The number of consecutive frames that must be identified as containing freezing in order to the
                     `moving` field for all those frames to False.
6. blur_kszie - The size of the Gaussian blur filter. For more information refer to:
                https://docs.opencv.org/master/d4/d13/tutorial_py_filtering.html.