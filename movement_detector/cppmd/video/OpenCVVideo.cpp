//
// Created by petioptrv on 2020-04-20.
//

#include <cstdlib>
#include <opencv2/core/hal/interface.h>

#include "OpenCVVideo.h"

OpenCVVideo::OpenCVVideo(const boost::filesystem::path &filePath) {
    vidPath = filePath;
    parseVidName();
    loadVideo();
}

double OpenCVVideo::getVidDuration() {
    double fps = video.get(cv::CAP_PROP_FPS);
    double frameCount = video.get(cv::CAP_PROP_FRAME_COUNT);
    double duration = frameCount / fps;

    return duration;
}

std::array<int, 2> OpenCVVideo::getFrameShape() {
    int width = (int) video.get(cv::CAP_PROP_FRAME_WIDTH);
    int height = (int) video.get(cv::CAP_PROP_FRAME_HEIGHT);
    std::array<int, 2> frameShape = {width, height};

    return frameShape;
}

double OpenCVVideo::getFrameRate() {
    double frameRate = video.get(cv::CAP_PROP_FPS);

    return frameRate;
}

void OpenCVVideo::setFramePos(int framePos) {
    video.set(cv::CAP_PROP_POS_FRAMES, framePos);
}

cv::Mat OpenCVVideo::getFrameAndAdvance() {
    cv::Mat frame;
    video.read(frame);

    return frame;
}

size_t OpenCVVideo::getFrameCount() {
    size_t frameCount = video.get(cv::CAP_PROP_FRAME_COUNT);

    return frameCount;
}

cv::Mat OpenCVVideo::getFrame(int idx) {
    setFramePos(idx);

    return getFrameAndAdvance();
}

double OpenCVVideo::getCurrentFramePos() {
    double framePos = video.get(cv::CAP_PROP_POS_MSEC);

    return framePos;
}

cv::Mat OpenCVVideo::getFramesSum() {
    setFramePos(0);
    cv::Mat currFrame;
    bool received = video.read(currFrame);
    int rows = currFrame.rows;
    int cols = currFrame.cols;
    int channels = currFrame.channels();
    cv::Mat sum(
            rows,
            cols,
            CV_64FC(channels),
            cv::Scalar::all(0)
    );

    while (received) {
        received = video.read(currFrame);
        if (received) {
            sum += currFrame;
        }
    }

    return sum;
}

void OpenCVVideo::parseVidName() {
    std::string vidPathStr = vidPath.string();
    std::size_t found = vidPathStr.rfind('/');

    if (found != std::string::npos) {
        std::size_t nameLen = vidPathStr.length() - found - 1;
        vidName = vidPathStr.substr(found + 1, nameLen);
    }
}

void OpenCVVideo::loadVideo() {
    std::string videoPathStr = vidPath.string();
    video.open(videoPathStr);
}
