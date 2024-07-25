cmake_minimum_required(VERSION 3.30)
project(PackageTest CXX)

find_package(mysql-concpp REQUIRED CONFIG)
add_executable(example src/example.cpp)

set(MYSQL_CONCPP_VAR "mysql::concpp")
set(MYSQL_CONCPP_VAR "${MYSQL_CONCPP_VAR}$<IF:$<BUILD_TYPE:STATIC>,_static$<ENDIF:>$<IF:$<CONFIG:Debug>,_debug$<ENDIF:>")

if(WIN32)
    target_link_libraries(example PRIVATE "${MYSQL_CONCPP_VAR}")
elseif(APPLE)
    target_link_libraries(example PRIVATE "${MYSQL_CONCPP_VAR}" resolv)
endif()
