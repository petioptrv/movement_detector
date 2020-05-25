add_library(catch2 catch.hpp main.cpp)
add_executable(video_tests test_video_opencv.cpp)
set_target_properties(video_tests PROPERTIES LINKER_LANGUAGE CXX)

target_link_libraries(video_tests catch2 video path_utils -lstdc++fs)

add_executable(path_util_tests test_path_utils.cpp)
find_package(Boost COMPONENTS regex)

target_link_libraries(path_util_tests catch2 path_utils ${Boost_LIBRARIES})
