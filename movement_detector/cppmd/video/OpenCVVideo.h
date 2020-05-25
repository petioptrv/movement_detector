//
// Created by petioptrv on 2020-04-20.
//

#ifndef MOVEMENT_DETECTOR_OPENCVVIDEO_H
#define MOVEMENT_DETECTOR_OPENCVVIDEO_H


#include <string>
#include <array>
#include <opencv2/opencv.hpp>
#include <boost/filesystem.hpp>

class OpenCVVideo {
public:
    explicit OpenCVVideo(const boost::filesystem::path &filePath);

    double getVidDuration();

    std::array<int, 2> getFrameShape();

    double getFrameRate();

    void setFramePos(int framePos);

    cv::Mat getFrameAndAdvance();

    size_t getFrameCount();

    cv::Mat getFrame(int idx);

    double getCurrentFramePos();

    cv::Mat getFramesSum();


private:
    boost::filesystem::path vidPath;
    std::string vidName;
    cv::VideoCapture video;


    void parseVidName();

    void loadVideo();
};


#endif //MOVEMENT_DETECTOR_OPENCVVIDEO_H
