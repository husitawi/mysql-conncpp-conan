cmake_minimum_required(VERSION 3.30)
project(PackageTest CXX)

find_package(mysql-concpp REQUIRED CONFIG)
add_executable(example src/example.cpp)
# mysql::concpp
# mysql::concpp-debug

# mysql::concpp-static
# mysql::concpp-static-debug

target_link_libraries(example PRIVATE mysql::concpp-static-debug)

# if(WIN32)
# elseif(APPLE)
#     target_link_libraries(example mysqlcppconn::mysqlcppconn resolv)
# endif()
