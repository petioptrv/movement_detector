//
// Created by petioptrv on 2020-05-03.
//

#include <boost/regex.hpp>

#include "path_utils.h"

boost::filesystem::path path_utils::getExeDir() {
    boost::filesystem::path full_path(boost::filesystem::current_path());
    return full_path;
}

boost::filesystem::path path_utils::getProjectDir() {
    boost::filesystem::path exe_path = path_utils::getExeDir();
    boost::regex path_match{R"(.+\/cppmd)"};

    boost::smatch project_dir_match;
    boost::regex_search(exe_path.string(), project_dir_match, path_match);

    return boost::filesystem::path(project_dir_match[0]);
}
