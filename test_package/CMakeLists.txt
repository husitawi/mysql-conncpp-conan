cmake_minimum_required(VERSION 3.30)
project(PackageTest CXX)

find_package(mysql-concpp REQUIRED CONFIG)
message(STATUS "MYSQL location: ${MYSQL_CONCPP_RUNTIME_LIBRARY_DIRS}")
add_executable(example src/example.cpp)
# target_link_libraries(example PRIVATE mysql::concpp-static-debug)
target_link_libraries(example PRIVATE mysql::concpp-static)

# if(WIN32)
#     message(STATUS "Copying DLLs: ${mysql-concpp_RUNTIME_LIBRARY_DIRS} ${mysql-concpp_RUNTIME_LIBRARY_DIR} ${MYSQL_CONCPP_RUNTIME_LIBRARY_DIRS}")
#     # add_custom_command(TARGET example POST_BUILD
#     #     COMMAND ${CMAKE_COMMAND} -E copy -t $<TARGET_FILE_DIR:example> $<TARGET_RUNTIME_DLLS:example>
#     #     COMMAND_EXPAND_LISTS
#     #     )

#     install(TARGETS example
#         COMPONENT example
#         RUNTIME_DEPENDENCIES
#         # PRE_EXCLUDE_REGEXES "api-ms-" "ext-ms-"
#         POST_EXCLUDE_REGEXES "${MYSQL_CONCPP_RUNTIME_LIBRARY_DIR}/.*\\.dll"
#         DIRECTORIES $<TARGET_FILE_DIR:example>)

# elseif(APPLE)
#     target_link_libraries(example mysqlcppconn::mysqlcppconn resolv)
# endif()
