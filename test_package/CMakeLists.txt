cmake_minimum_required(VERSION 3.30)
project(PackageTest CXX)

find_package(mysql-concpp REQUIRED CONFIG)
add_executable(example src/example.cpp)

set(MYSQL_CONCPP_VAR "mysql::concpp")
target_link_libraries(example PRIVATE "${MYSQL_CONCPP_VAR}-static-debug")