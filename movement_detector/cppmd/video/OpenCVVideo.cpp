//
// Created by petioptrv on 2020-04-20.
//

#include "OpenCVVideo.h"
#include <cstdlib>


OpenCVVideo::OpenCVVideo(const std::string &filePath) {
    vidPath = filePath;
    vidName = parseVidName(filePath);
    loadVideo();
}

std::string OpenCVVideo::parseVidName(const std::string &filePath) {
    std::size_t found = filePath.rfind('/');
    std::string vidName;

    if (found != std::string::npos) {
        std::size_t nameLen = filePath.length() - found;
        vidName = filePath.substr(found, nameLen);
    }

    return vidName;
}

void OpenCVVideo::loadVideo() {
    video.open()
}
