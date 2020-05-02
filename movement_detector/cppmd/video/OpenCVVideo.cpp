//
// Created by petioptrv on 2020-04-20.
//

#include "OpenCVVideo.h"
#include <cstdlib>


OpenCVVideo::OpenCVVideo(const std::string &filePath) {
    vidPath = filePath;
    parseVidName(filePath);
    loadVideo();
}

float OpenCVVideo::getVidDuration() {
}

void OpenCVVideo::parseVidName(const std::string &filePath) {
    std::size_t found = filePath.rfind('/');

    if (found != std::string::npos) {
        std::size_t nameLen = filePath.length() - found;
        vidName = filePath.substr(found, nameLen);
    }
}

void OpenCVVideo::loadVideo() {
    video.open(vidPath);
}
