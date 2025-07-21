cmake_minimum_required(VERSION 3.10.0)

project(ROBOCALLEE_FMS VERSION 0.1.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)

# 경로 설정
set(LIB_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/lib/include")
set(INCLUDE_DIR "${CMAKE_SOURCE_DIR}/include")
set(UTILE_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/Utile/")
set(LOGGER_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/Utile/include")

set(OpenCV_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/lib/opencv/include")
set(OpenCV_LIB_DIR "${CMAKE_SOURCE_DIR}/lib/opencv/bin")

set(LIB_BIN_DIR "${CMAKE_SOURCE_DIR}/lib/bin")

# include 경로 등록
include_directories(
	${LIB_INCLUDE_DIR}
	${INCLUDE_DIR}
	${UTILE_INCLUDE_DIR}
    ${LOGGER_INCLUDE_DIR}
	)
    
# 라이브러리 경로 등록
link_directories(${OpenCV_LIB_DIR})

add_executable(ROBOCALLEE_FMS
    main.cpp
    src/Core.cpp
    src/AmrAdapter.cpp
    src/TaskManager.cpp
    Utile/Logger/src/Logger.cpp
)

# 필요한 OpenCV 모듈 수동 연결 (필요한 .a/.so 파일 이름만 작성)
target_link_libraries(ROBOCALLEE_FMS
    opencv_core
    opencv_imgproc
    opencv_highgui
    opencv_imgcodecs
    opencv_videoio
    opencv_calib3d
    opencv_objdetect
    opencv_aruco
)
	
