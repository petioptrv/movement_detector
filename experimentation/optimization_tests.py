import os
import time
import queue
import multiprocessing as mlpr
import threading as mltr
import math

import numpy as np
import cv2
import pims
import asyncio

from src.video.video import CvVideo


BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
video_name = 'flashing_light.mp4'
video_path = os.path.join(BASE_PATH, 'videos', video_name)


async def frame_fetch(vid: cv2.VideoCapture, queue: asyncio.Queue):
    while True:
        ret, frame = vid.read()
        if ret:
            await queue.put(frame)
        else:
            break


async def frame_sum(frame_sum, queue: asyncio.Queue):
    frame_sum += await queue.get()


def que_frames(cv2_vid: cv2.VideoCapture, thread_queue: queue.Queue):
    while True:
        ret, frame = cv2_vid.read()
        if ret:
            thread_queue.put((ret, frame))
        else:
            thread_queue.put((ret, frame))
            break


def video_traversal_cv2_vs_pims():
    print('\n\n------------ Video traversal OpenCV vs PIMS ------------\n')

    cv2_vid = cv2.VideoCapture(video_path)
    cv2_frames_count = cv2_vid.get(cv2.CAP_PROP_FRAME_COUNT)
    cv2_frames_subset = int(cv2_frames_count / 20)
    pims_vid = pims.open(video_path)

    # OpenCV regular video traversal
    start_time = time.time()
    while True:
        ret, frame = cv2_vid.read()
        if not ret:
            break
    print('OpenCV regular video traversal: {:.2f}s'.format(time.time() - start_time))

    cv2_vid = cv2.VideoCapture(video_path)
    # OpenCV index-based video traversal
    start_time = time.time()
    for i in range(cv2_frames_subset):
        cv2_vid.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cv2_vid.read()
        if i == cv2_frames_subset - 1:
            print('OpenCV read %{:.2f} of the frames in {:.2f}s'.format(
                i / cv2_frames_count * 100, time.time() - start_time)
            )
            break

    # PIMS index-based video traversal
    start_time = time.time()
    for _frame in pims_vid:
        frame = _frame
    print('PIMS video traversal: {:.2f}'.format(time.time() - start_time))


def async_video_traversals():
    print('\n\n--- Async video traversal OpenCV vs PIMS, mlpr vs mltr ---\n')

    # cv2_vid = cv2.VideoCapture(video_path)
    # cv2_height = int(cv2_vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # cv2_width = int(cv2_vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    # sum_frame_sync = np.zeros((cv2_height, cv2_width, 3), dtype=np.uint32)
    # start_time = time.time()
    # while True:
    #     ret, frame = cv2_vid.read()
    #     if ret:
    #         sum_frame_sync += frame
    #     else:
    #         break
    # print('Sync cv2 frames sum: {:.2f}s'.format(time.time() - start_time))
    # cv2_vid = cv2.VideoCapture(video_path)
    # sum_frame_mltr = np.zeros((cv2_height, cv2_width, 3), dtype=np.int64)
    # frames_queue = queue.Queue()
    # mltr_thread = mltr.Thread(target=que_frames, args=(cv2_vid, frames_queue))
    # start_time = time.time()
    # mltr_thread.start()
    # while True:
    #     ret, frame = frames_queue.get()
    #     if ret:
    #         sum_frame_mltr += frame
    #     else:
    #         break
    # print('Async cv2 frames sum mltr: {:.2f}s'.format(time.time() - start_time))
    # cv2_vid = cv2.VideoCapture(video_path)
    # sum_frames_mlpr = np.zeros((cv2_height, cv2_width, 3), dtype=np.int64)
    # frames_queue = mlpr.Queue()
    # mlpr_thread = mlpr.Process(target=que_frames, args=(cv2_vid, frames_queue))
    # start_time = time.time()
    # mlpr_thread.start()
    # while True:
    #     ret, frame = frames_queue.get()
    #     if ret:
    #         sum_frames_mlpr += frame
    #     else:
    #         break
    # print('Async cv2 frames sum mlpr: {:.2f}s'.format(time.time() - start_time))
    # cv2_vid = cv2.VideoCapture(video_path)
    # sum_frames_async = np.zeros((cv2_height, cv2_width, 3), dtype=np.int64)
    # frames_queue = asyncio.Queue()
    # start_time = time.time()
    # fetch_task = asyncio.create_task(frame_fetch(cv2_vid, frames_queue))
    # sum_task = asyncio.create_task(frame_sum(sum_frames_async, frames_queue))
    # await fetch_task
    # await sum_task
    # print('Async cv2 frames sum asyncio: {:.2f}s'.format(time.time() - start_time))
    start_time = time.time()
    cust_vid = CvVideo('/Users/petioptrv/Documents/Programming/Python/movement_detector/videos/flashing_light.mp4')
    sum_frames_cust = sum(cust_vid)
    print('Custom frames sum: {:.2f}s'.format(time.time() - start_time))
    print('Equality of frames:', np.all(sum_frame_sync == sum_frames_cust))


if __name__ == '__main__':
    async_video_traversals()
