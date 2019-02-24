import cv2

video_path = 'videos/Rat Flashing light.wmv'
cam = cv2.VideoCapture(video_path)


def skip_frames(x: int) -> None:
    """
    Skips X frames
    :param x: number of frames to skip
    """
    for i in range(0, x):
        cam.read()

def merge_frames(frames):
    """
    Merges 3 frames together. This can be used for motion blur or to remove flicker.
    :param: frames array of frames to merge
    :return: the merged frames
    """

    if len(frames) < 2:
        return None
    frac = 1/len(frames)
    output = cv2.addWeighted(frames[0], frac, frames[1], frac, 0)

    for i in range(2, len(frames)):
        output = cv2.addWeighted(output, i/len(frames), frames[i], frac, 0)
    return output

skip_frames(4005)

frames = []
frame_id = -1

# initialise the array (we will be reading at least 4 frames at a time so they need to be in the array)
frames_to_analyse = 4
for i in range(0, frames_to_analyse):
    frame_id += 1
    ret, frame = cam.read()
    frames += [frame]


while 1:
    frame_id += 1
    ret, frame = cam.read()  # read the current frame
    display_frame = frame
    frames += [frame]

    if not ret:  # break if there is no frame left
        break

    merged = merge_frames([frame, frames[frame_id - 1], frames[frame_id - 2], frames[frame_id - 3], frames[frame_id - 4]])

    cv2.imshow('frame', frame)
    cv2.imshow('de-flickered', merged)
    key = cv2.waitKey() & 0xFF
    if key == ord("q"):
        break
cv2.destroyAllWindows()
print('end')
