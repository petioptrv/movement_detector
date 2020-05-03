cmake_minimum_required(VERSION 3.10)

project(movement_detector)

add_subdirectory(video)
add_subdirectory(tests)

add_library(path_utils path_utils.cpp path_utils.h)
find_package(Boost COMPONENTS filesystem regex)
include_directories(${Boost_INCLUDE_DIRS})

target_link_libraries(path_utils ${Boost_LIBRARIES})
