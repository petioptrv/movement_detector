file(GLOB VIDEO_EXECUTABLES
        "*.h"
        "*.cpp"
        )

find_package(Boost COMPONENTS filesystem regex)
include_directories(${Boost_INCLUDE_DIRS})

add_library(video ${VIDEO_EXECUTABLES} ${Boost_LIBRARIES})
find_package( OpenCV 4.3.0 REQUIRED )

target_link_libraries(video ${OpenCV_LIBS})