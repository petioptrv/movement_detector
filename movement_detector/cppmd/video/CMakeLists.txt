file(GLOB VIDEO_EXECUTABLES
        "*.h"
        "*.cpp"
        )

add_executable(video ${VIDEO_EXECUTABLES})
find_package( OpenCV REQUIRED )

target_link_libraries(video ${OpenCV_LIBS})