cmake_minimum_required(VERSION 2.8)

include(${CMAKE_CURRENT_SOURCE_DIR}/helpers.cmake)


project(smithproxy_auth)

SET(CMAKE_SOURCE_DIR "src/")
SET(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}")

include_directories ("${PROJECT_SOURCE_DIR}/src/")



if(EXISTS "${PROJECT_SOURCE_DIR}/.git")
    execute_process(
            COMMAND git rev-parse --abbrev-ref HEAD
            WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
            OUTPUT_VARIABLE SX_GIT_BRANCH
            OUTPUT_STRIP_TRAILING_WHITESPACE
    )

    execute_process(
            COMMAND git log -1 --format=%h
            WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
            OUTPUT_VARIABLE SX_GIT_COMMIT_HASH
            OUTPUT_STRIP_TRAILING_WHITESPACE
    )

    execute_process(
            COMMAND git describe --tags --dirty
            WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
            OUTPUT_VARIABLE SX_GIT_VERSION
            OUTPUT_STRIP_TRAILING_WHITESPACE
    )

else(EXISTS "${PROJECT_SOURCE_DIR}/.git")
    set(SX_GIT_BRANCH "")
    set(SX_GIT_COMMIT_HASH "")
    set(SX_GIT_VERSION "")

endif(EXISTS "${PROJECT_SOURCE_DIR}/.git")

message(STATUS "Git current smithproxy branch: ${SX_GIT_BRANCH}")
message(STATUS "Git commit smithrproxy hash: ${SX_GIT_COMMIT_HASH}")
message(STATUS "Git commit smithrproxy version: ${SX_GIT_VERSION}")

message(STATUS "Generating smithproxy_version.h")

configure_file(
        ${PROJECT_SOURCE_DIR}/src/smithproxy_version.h.in
        ${PROJECT_SOURCE_DIR}/src/smithproxy_version.h
)


set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}")

include(${CMAKE_CURRENT_SOURCE_DIR}/install.cmake)
