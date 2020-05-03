//
// Created by petioptrv on 2020-05-03.
//

#include <iostream>
#include <catch2/catch.hpp>
#include <boost/regex.hpp>

#include "../path_utils.h"

TEST_CASE("Test getting current exec dir", "[path_basic]") {
    boost::filesystem::path exe_dir = path_utils::getExeDir();
    boost::regex path_match{R"(.+\/cppmd\/.+\/tests)"};

    REQUIRE(boost::regex_match(exe_dir.string(), path_match));
}

TEST_CASE("Test getting project dir", "[path_basic]") {
    boost::filesystem::path project_dir = path_utils::getProjectDir();
    boost::regex path_match(R"(.+\/cppmd)");
    boost::regex anti_pattern(R"(.+\/cppmd.+)");

    REQUIRE(boost::regex_match(project_dir.string(), path_match));
    REQUIRE(!boost::regex_match(project_dir.string(), anti_pattern));
}
