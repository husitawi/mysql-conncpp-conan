cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(mysqlcppconn REQUIRED)
find_package(boost REQUIRED)
# message(STATUS "mysqlcppconn_INCLUDE_DIRS=${mysqlcppconn_INCLUDE_DIRS}")
# message(STATUS "mysqlcppconn_LIBRARIES=${mysqlcppconn_LIBRARIES}")

add_executable(example src/example.cpp)
# Check if Apple
if (CMAKE_HOST_APPLE)
    target_link_libraries(example PRIVATE mysqlcppconn::cppconn Boost::boost resolv)
else()
    target_link_libraries(example PRIVATE mysqlcppconn::cppconn Boost::boost)
endif()

