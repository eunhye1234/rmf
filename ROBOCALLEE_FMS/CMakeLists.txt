cmake_minimum_required(VERSION 3.10.0)

project(ROBOCALLEE_FMS VERSION 0.1.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)

# 경로 설정
set(LIB_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/lib/include")
set(INCLUDE_DIR "${CMAKE_SOURCE_DIR}/include")
set(UTILE_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/Utile/")
set(LOGGER_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/Utile/include")

set(LIB_BIN_DIR "${CMAKE_SOURCE_DIR}/lib/bin")

# include 경로 등록
include_directories(
	${LIB_INCLUDE_DIR}
	${INCLUDE_DIR}
	${UTILE_INCLUDE_DIR}
    ${LOGGER_INCLUDE_DIR}
	)
    
add_executable(ROBOCALLEE_FMS
    main.cpp
    src/Core.cpp
    src/AmrAdapter.cpp
    src/TaskManager.cpp
    Utile/Logger/src/Logger.cpp
)
	
