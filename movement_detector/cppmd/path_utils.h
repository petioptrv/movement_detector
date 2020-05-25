//
// Created by petioptrv on 2020-05-03.
//

#ifndef MOVEMENT_DETECTOR_PATHUTILS_H
#define MOVEMENT_DETECTOR_PATHUTILS_H

#include <boost/filesystem.hpp>

namespace path_utils {
    boost::filesystem::path getExeDir();

    boost::filesystem::path getProjectDir();
};


#endif //MOVEMENT_DETECTOR_PATHUTILS_H
