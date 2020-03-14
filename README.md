# Movement Detector

INSTALLATION (MAC)

1. Install Python 3 for your operating system. (https://www.python.org/downloads/)
2. Open a Terminal window.
3. Type "chmod 700 path/to/file/run" where the part following "chmod 700" is the path to the file called "run". 
4. Hit Enter.

RUN

1. Open a Terminal window.
2. Drag and drop the file called "run" onto the terminal window.
3. Hit Enter.

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
2. Execute the instructions in the RUN section.
3. Results will be in the "analysis" folder.
