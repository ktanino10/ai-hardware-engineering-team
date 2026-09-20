cmake_minimum_required(VERSION 3.16)

set(IDF_TARGET "esp32s3")
set(PROJECT_VER "n8r8-eval-rev5-m1")
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
get_filename_component(REV5_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
include("${CMAKE_CURRENT_LIST_DIR}/source-contract.cmake")

execute_process(COMMAND git -C "$ENV{IDF_PATH}" rev-parse HEAD
                OUTPUT_VARIABLE sdk_commit OUTPUT_STRIP_TRAILING_WHITESPACE
                RESULT_VARIABLE sdk_result)
if(NOT sdk_result EQUAL 0 OR NOT sdk_commit STREQUAL "30aaf64524299d3bde422ca9a2848090d1bc5d0f")
    message(FATAL_ERROR "Use the locked official ESP-IDF v5.5.2 commit.")
endif()

# Reuse the original component registration and C sources, including all guards.
set(EXTRA_COMPONENT_DIRS "${REV5_ROOT}/measurement/main")
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
idf_build_set_property(MINIMAL_BUILD ON)
project(rev5_n8r8_evaluation)

idf_component_get_property(measurement_component main COMPONENT_DIR)
if(NOT measurement_component STREQUAL "${REV5_ROOT}/measurement/main")
    message(FATAL_ERROR "Evaluation must build the unchanged measurement/main component.")
endif()
if(NOT CONFIG_IDF_TARGET_ESP32S3 OR
   NOT CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ EQUAL 80 OR
   NOT CONFIG_FREERTOS_HZ EQUAL 1000 OR
   NOT CONFIG_ESP_CONSOLE_UART_NUM EQUAL 0 OR
   NOT CONFIG_ESP_CONSOLE_UART_BAUDRATE EQUAL 115200 OR
   NOT CONFIG_ESPTOOLPY_FLASHMODE_DIO OR
   NOT CONFIG_ESPTOOLPY_FLASHFREQ_40M OR
   NOT CONFIG_ESPTOOLPY_FLASHSIZE_8MB OR
   NOT CONFIG_PARTITION_TABLE_SINGLE_APP)
    message(FATAL_ERROR "Resolved settings differ from the bounded N8R8 evaluation profile.")
endif()
if(CONFIG_SPIRAM OR CONFIG_PM_ENABLE OR CONFIG_BT_ENABLED OR CONFIG_ESP_WIFI_ENABLED OR
   CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG_ENABLED OR CONFIG_ESP_CONSOLE_USB_CDC)
    message(FATAL_ERROR "PSRAM, DFS, radio and native USB console are outside this evaluation.")
endif()
message(STATUS "N8R8 evaluation only: PSRAM unused; NOT_FOR_FLASH, not module adoption.")
