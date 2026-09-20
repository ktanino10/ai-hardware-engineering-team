idf_component_register(
    SRCS "main.c" "../vendor/bosch/bmi2.c" "../vendor/bosch/bmi270.c"
    INCLUDE_DIRS "." "../vendor/bosch" "../../preparation/generated"
    REQUIRES esp_driver_gpio esp_driver_spi esp_driver_uart esp_timer
)
set_source_files_properties("main.c" PROPERTIES COMPILE_OPTIONS "-Wall;-Wextra;-Werror")
