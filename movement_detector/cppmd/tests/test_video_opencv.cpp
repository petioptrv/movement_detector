//
// Created by petioptrv on 2020-05-02.
//

#include "catch.hpp"

#include "../video/OpenCVVideo.h"
#include "../path_utils.h"

bool compareFrames(cv::Mat first, cv::Mat second) {
    cv::Mat compars;
    cv::absdiff(first, second, compars);
    cv::Scalar sum = cv::sum(compars);
    int nonZero = cv::countNonZero(sum);
    bool equal = nonZero == 0;
    return equal;
}

TEST_CASE("Test retrieving opencv video functionality", "[opencv_vid]") {
    // The video is currently created using the utils in the pytest conf file.
    // Frames are [10, 20, 30, 40, 50] * 30
    // TODO: define the video-creation process

    boost::filesystem::path project_dir = path_utils::getProjectDir();
    boost::filesystem::path test_vid_path = (
            project_dir / "tests" / "videos" / "test_vid.mp4"
    );
    OpenCVVideo testVid(test_vid_path);

    SECTION("Test retrieving video frame shape") {
        std::array<int, 2> vidShape = testVid.getFrameShape();

        REQUIRE(vidShape[0] == 250);
        REQUIRE(vidShape[1] == 250);
    }

    SECTION("Test retrieving video duration") {
        double vid_duration = testVid.getVidDuration();

        REQUIRE(vid_duration == 5);
    }

    SECTION("Test retrieving video frame rate") {
        double frameRate = testVid.getFrameRate();

        REQUIRE(frameRate == 30);
    }

    SECTION("Test frame position set, frame retrieval, get frame by index") {
        testVid.setFramePos(0);
        cv::Mat firstFrame = testVid.getFrameAndAdvance();

        cv::Mat frameValidator = testVid.getFrame(0);

        REQUIRE(compareFrames(firstFrame, frameValidator));

        testVid.setFramePos(1);
        cv::Mat nextFrame = testVid.getFrameAndAdvance();

        REQUIRE(!compareFrames(firstFrame, nextFrame));

        frameValidator = testVid.getFrame(1);

        REQUIRE(compareFrames(nextFrame, frameValidator));
    }

    SECTION("Test frames sum") {
        cv::Mat frameSum = testVid.getFramesSum();
        cv::Mat reffFrame(
                frameSum.rows,
                frameSum.cols,
                CV_64FC(frameSum.channels()),
                cv::Scalar::all(4459)
        );
        cv::Scalar compar = cv::sum(frameSum == reffFrame);

        REQUIRE(compar[0] == (250 * 250 * 255));  // TODO: fix this test case...
    }
}

