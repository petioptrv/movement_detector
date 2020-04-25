//
// Created by petioptrv on 2020-04-20.
//

#ifndef MOVEMENT_DETECTOR_OPENCVVIDEO_H
#define MOVEMENT_DETECTOR_OPENCVVIDEO_H


#include <string>
#include <array>
#include <opencv2/videoio.hpp>

class OpenCVVideo {
public:
    explicit OpenCVVideo(const std::string &filePath);

    float getVidDuration();

    std::array<int, 2> getFrameShape();


private:
    std::string vidPath;
    std::string vidName;
    cv::VideoCapture video;


    static std::string parseVidName(const std::string &filePath);

    void loadVideo();
};


#endif //MOVEMENT_DETECTOR_OPENCVVIDEO_H
