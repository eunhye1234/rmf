cmake_minimum_required(VERSION 3.5)
project(zmq_vision_follower)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)

# install(
#   PROGRAMS
#   zmq_vision_follower/zmq_vision_follower.py
#   DESTINATION lib/${PROJECT_NAME}
# )
ament_python_install_package(${PROJECT_NAME})

ament_package()
