cmake_minimum_required(VERSION 3.10.0)

project(ROBOCALLEE_FMS VERSION 0.1.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)

# 경로 설정
set(ADAPTERS_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/Adapters/include")
set(CORE_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/Core/include")
set(LIB_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/lib")
set(REQUEST_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/Request/include")
set(ROSINTERFACE_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/RosInterface/include")
set(TASK_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/Task/include")
set(TRAFFIC_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/Traffic/include")
set(LOGGER_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/Utile/Logger/include")
set(UTILE_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/Utile/include")

# include 경로 등록
include_directories(
	${ADAPTERS_INCLUDE_DIR}
	${CORE_INCLUDE_DIR}
	${LIB_INCLUDE_DIR}
    ${REQUEST_INCLUDE_DIR}
    ${ROSINTERFACE_INCLUDE_DIR}
    ${TASK_INCLUDE_DIR}
    ${TRAFFIC_INCLUDE_DIR}
    ${UTILE_INCLUDE_DIR}
    ${LOGGER_INCLUDE_DIR}
	)

add_executable(ROBOCALLEE_FMS
    main.cpp
    Utile/Logger/src/Logger.cpp
    Core/src/Core.cpp
    Task/src/Dispatcher.cpp
    Task/src/Executor.cpp
)

# 라이브러리 경로 등록
# link_directories(${OpenCV_LIB_DIR})

# 필요한 OpenCV 모듈 수동 연결 (필요한 .a/.so 파일 이름만 작성)
# target_link_libraries(ROBOCALLEE_FMS
#     opencv_core
#     opencv_imgproc
#     opencv_highgui
#     opencv_imgcodecs
#     opencv_videoio
#     opencv_calib3d
#     opencv_objdetect
#     opencv_aruco
# )
