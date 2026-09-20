cmake_minimum_required(VERSION 3.16)
set(IDF_TARGET "esp32s3")
set(PROJECT_VER "rev5-m1")
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
file(SHA256 "${CMAKE_CURRENT_LIST_DIR}/../preparation/generated/pin_definitions.h" pin_hash)
if(NOT pin_hash STREQUAL "00bb53739d3f90278e09c7813cd1ca56c11c0e8e79e5e7bd171ad16a3c29ea2a")
    message(FATAL_ERROR "Frozen Rev5 generated pin definitions changed; rebind through the owner.")
endif()
execute_process(COMMAND git -C "$ENV{IDF_PATH}" rev-parse HEAD
                OUTPUT_VARIABLE sdk_commit OUTPUT_STRIP_TRAILING_WHITESPACE
                RESULT_VARIABLE sdk_result)
if(NOT sdk_result EQUAL 0 OR NOT sdk_commit STREQUAL "30aaf64524299d3bde422ca9a2848090d1bc5d0f")
    message(FATAL_ERROR "Use the locked official ESP-IDF v5.5.2 commit.")
endif()
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
# Fixed SDK tools/cmake/project.cmake: build main and its required closure only.
idf_build_set_property(MINIMAL_BUILD ON)
project(rev5_measurement)
