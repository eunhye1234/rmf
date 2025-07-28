cmake_minimum_required(VERSION 3.10.0)

project(robocallee_fms VERSION 0.1.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)

#GCC or Clang
#-Wall: 기본 경고 전부 표시
#-Wextra: 추가 경고
#-Wpedantic: 표준에 어긋나는 코드도 경고

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 경로 설정
set(ADAPTERS_INCLUDE_DIR    "${CMAKE_SOURCE_DIR}/Adapters/include")
set(CORE_INCLUDE_DIR        "${CMAKE_SOURCE_DIR}/Core/include")
set(LIB_INCLUDE_DIR         "${CMAKE_SOURCE_DIR}/lib")
set(REQUEST_INCLUDE_DIR     "${CMAKE_SOURCE_DIR}/Request/include")
set(INTERFACE_INCLUDE_DIR   "${CMAKE_SOURCE_DIR}/Interface/include")
set(TASK_INCLUDE_DIR        "${CMAKE_SOURCE_DIR}/Task/include")
set(TRAFFIC_INCLUDE_DIR     "${CMAKE_SOURCE_DIR}/Traffic/include")
# set(LOGGER_INCLUDE_DIR      "${CMAKE_SOURCE_DIR}/../Utile/Logger/include")
# set(UTILE_INCLUDE_DIR       "${CMAKE_SOURCE_DIR}/../Utile/include")
# set(COMMON_INCLUDE_DIR      "${CMAKE_SOURCE_DIR}/../Utile/Common/include")

find_package(ament_cmake REQUIRED)  # ament 빌드시스템 사용
find_package(rclcpp REQUIRED)       # ROS2 C++ 클라이언트 라이브러리
find_package(std_msgs REQUIRED)     # 표준 메시지 타입들 (e.g. std_msgs::String)

# include 경로 등록
include_directories(
	${ADAPTERS_INCLUDE_DIR}
	${CORE_INCLUDE_DIR}
	${LIB_INCLUDE_DIR}
  ${REQUEST_INCLUDE_DIR}
  ${INTERFACE_INCLUDE_DIR}
  ${TASK_INCLUDE_DIR}
  ${TRAFFIC_INCLUDE_DIR}
  ${UTILE_INCLUDE_DIR}
  ${LOGGER_INCLUDE_DIR}
  ${COMMON_INCLUDE_DIR}
	)

add_executable(robocallee_fms
    main.cpp
    # ../Utile/Logger/src/Logger.cpp
    Core/src/Core.cpp
    Task/src/Dispatcher.cpp
    Task/src/Executor.cpp
    Interface/src/RosInterface.cpp
    Adapters/src/AmrAdapter.cpp
    Adapters/src/RobotArmAdapter.cpp
    Request/src/RequestManager.cpp      #추가
)

#라이브러리 경로 등록
link_directories(${OpenCV_LIB_DIR})

#필요한 OpenCV 모듈 수동 연결 (필요한 .a/.so 파일 이름만 작성)
target_link_libraries(robocallee_fms
    PUBLIC
    rclcpp::rclcpp ${std_msgs_TARGETS}
)

install(TARGETS
  robocallee_fms
  DESTINATION lib/${PROJECT_NAME})

ament_package()