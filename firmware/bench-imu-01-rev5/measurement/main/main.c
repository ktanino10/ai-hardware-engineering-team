/*
 * Rev5 measurement-only bring-up. NOT EXECUTED ON HARDWARE.
 *
 * Pin authority: committed preparation/generated/pin_definitions.h and
 * integrated Circuit REV5-INT-WIP-3F-U1, not the old STM32 project.
 * DS-IMU-079..088/094/098..100: BMI270 identity, SPI framing/init/raw data.
 * DS-MCU-101/102/129/140: adopted N8R2 and actual UART0/module pins.
 * Additional exact official SDK/API locators and hashes: source-lock.json.
 *
 * No motor/control/I2C/arm/radio/USB app/physical-unit conversion.
 * The unmodified Bosch driver contains optional APIs; this application does
 * not call compensation, remapping, FOC, self-test, FIFO, NVM or CRT APIs.
 */
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "sdkconfig.h"
#include "driver/gpio.h"
#include "driver/spi_master.h"
#include "driver/uart.h"
#include "esp_err.h"
#include "esp_rom_sys.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "soc/soc_caps.h"
#include "soc/uart_pins.h"

#include "bmi270.h"
#include "pin_definitions.h"

#define ARRAY_COUNT(a) (sizeof(a) / sizeof((a)[0]))
#define SENSOR_COUNT 6
#define MEASUREMENT_HOST SPI2_HOST
#define SPI_HZ 1000000
#define SPI_TIMEOUT_MS 100
#define SPI_DATA_LIMIT 64
#define CONFIG_CHUNK_BYTES 32
#define LOG_LINE_LIMIT 512
#define LOG_TIMEOUT_US INT64_C(100000)
#define SCAN_PERIOD_US UINT32_C(500000)
#define PROFILE_ID "rev5-m1"

#if !CONFIG_IDF_TARGET_ESP32S3
#error "This project is only for the source-bound ESP32-S3-WROOM-1-N8R2."
#endif
#if defined(CONFIG_PM_ENABLE) || defined(CONFIG_SPIRAM)
#error "This measurement profile does not use DFS/sleep or PSRAM."
#endif
#if defined(CONFIG_BT_ENABLED) || defined(CONFIG_ESP_WIFI_ENABLED)
#error "No radio component is permitted in this measurement application."
#endif
#if defined(CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG_ENABLED) || defined(CONFIG_ESP_CONSOLE_USB_CDC)
#error "Only the actual source-bound UART0 console is allowed."
#endif
_Static_assert(CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ == 80, "Clock profile changed");
_Static_assert(CONFIG_FREERTOS_HZ == 1000, "Delay rounding assumes 1 ms ticks");
_Static_assert(CONFIG_ESP_CONSOLE_UART_NUM == 0, "Source uses UART0");
_Static_assert(CONFIG_ESP_CONSOLE_UART_BAUDRATE == 115200, "Source framing changed");
_Static_assert(REV5_PIN_UART0_TX_GPIO == U0TXD_GPIO_NUM, "UART console/pin source mismatch");
_Static_assert(REV5_PIN_UART0_RX_GPIO == U0RXD_GPIO_NUM, "UART console/pin source mismatch");
_Static_assert(SOC_SPI_PERIPH_CS_NUM(MEASUREMENT_HOST) >= SENSOR_COUNT,
               "This SDK/target does not provide the six required hardware CS slots");
_Static_assert(ARRAY_COUNT(rev5_preparation_imus) == SENSOR_COUNT, "IMU source count changed");
_Static_assert(SPI_DATA_LIMIT <= SOC_SPI_MAXIMUM_BUFFER_SIZE, "Non-DMA FIFO limit");
_Static_assert(CONFIG_CHUNK_BYTES % 2 == 0, "Bosch upload uses word offsets");

/* Every driven CS is a committed REV5_PIN_* macro, not a second pin map. */
static const gpio_num_t cs_pins[SENSOR_COUNT] = {
    REV5_PIN_IMU_CS_X_A_GPIO, REV5_PIN_IMU_CS_X_B_GPIO,
    REV5_PIN_IMU_CS_Y_A_GPIO, REV5_PIN_IMU_CS_Y_B_GPIO,
    REV5_PIN_IMU_CS_Z_A_GPIO, REV5_PIN_IMU_CS_Z_B_GPIO
};

typedef struct {
    const rev5_preparation_imu_identity *identity;
    gpio_num_t cs;
    struct bmi2_dev dev;
    spi_device_handle_t spi;
    /* Static lifetime is essential if get_trans_result times out. Neither
     * descriptor nor buffers may then point to the SensorAPI's stack. */
    spi_transaction_t transaction;
    uint8_t tx[SPI_DATA_LIMIT];
    uint8_t rx[SPI_DATA_LIMIT];
    bool pending;
    bool ready;
    bool chip_observed;
    bool internal_observed;
    uint8_t chip;
    uint8_t internal;
    int spi_khz;
    esp_err_t bus_error;
    int8_t api_error;
    const char *failure;
} sensor_t;

static sensor_t sensors[SENSOR_COUNT];
static uint64_t log_sequence;
static uint32_t dropped_lines;
static uint32_t overrun_count;
static bool uart_needs_lf;

/* esp_rom_delay_us takes microseconds. Long waits yield; +1 tick prevents
 * a call near a tick edge from shortening the manufacturer's requested
 * interval. Longer scheduler delays are allowed, never timing proof.
 * Bosch's misleading *_READ_DELAY_MS macro is passed by Bosch to delay_us:
 * its value 20000 is therefore 20000 us, not 20000 ms. (bmi2.c:5218.) */
static void sensor_delay_us(uint32_t us, void *intf_ptr)
{
    (void)intf_ptr;
    if (us >= 2000) {
        vTaskDelay(pdMS_TO_TICKS((us + 999) / 1000) + 1);
    } else {
        esp_rom_delay_us(us);
    }
}

/* First select ALL SIX with SCK/MOSI quiescent. DS-IMU-098/099 and
 * Circuit design-rationale 3.2: do not clock one initialized device while
 * the other five shared SDx pins still act as I2C SDA.
 * No rail-good sense exists: this wait is not proof of valid power. */
static esp_err_t select_all_spi_quiescent(void)
{
    uint64_t mask = (UINT64_C(1) << REV5_PIN_IMU_SCK_GPIO) |
                    (UINT64_C(1) << REV5_PIN_IMU_MOSI_GPIO);
    esp_err_t err;
    for (size_t i = 0; i < SENSOR_COUNT; ++i) {
        if (cs_pins[i] != (gpio_num_t)rev5_preparation_imus[i].host_gpio) {
            return ESP_ERR_INVALID_STATE;
        }
        mask |= UINT64_C(1) << cs_pins[i];
        /* Load inactive latch before enabling its output driver. */
        if ((err = gpio_set_level(cs_pins[i], 1)) != ESP_OK) {
            return err;
        }
    }
    if ((err = gpio_set_level(REV5_PIN_IMU_SCK_GPIO, 0)) != ESP_OK ||
        (err = gpio_set_level(REV5_PIN_IMU_MOSI_GPIO, 0)) != ESP_OK) {
        return err;
    }
    const gpio_config_t cfg = {
        .pin_bit_mask = mask,
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    if ((err = gpio_config(&cfg)) != ESP_OK) {
        return err;
    }
    sensor_delay_us(2000, NULL);
    for (size_t i = 0; i < SENSOR_COUNT; ++i) {
        if ((err = gpio_set_level(cs_pins[i], 0)) != ESP_OK) {
            return err;
        }
        /* Owner margin, not a new manufacturer minimum CS pulse length. */
        sensor_delay_us(2, NULL);
        if ((err = gpio_set_level(cs_pins[i], 1)) != ESP_OK) {
            return err;
        }
        sensor_delay_us(200, NULL);
    }
    return ESP_OK;
}

static esp_err_t measurement_bus_init(void)
{
    const spi_bus_config_t bus = {
        .mosi_io_num = REV5_PIN_IMU_MOSI_GPIO,
        .miso_io_num = REV5_PIN_IMU_MISO_GPIO,
        .sclk_io_num = REV5_PIN_IMU_SCK_GPIO,
        .quadwp_io_num = -1, .quadhd_io_num = -1,
        .data4_io_num = -1, .data5_io_num = -1,
        .data6_io_num = -1, .data7_io_num = -1,
        .data_io_default_level = false,
        .max_transfer_sz = SPI_DATA_LIMIT,
        .flags = SPICOMMON_BUSFLAG_MASTER
    };
    return spi_bus_initialize(MEASUREMENT_HOST, &bus, SPI_DMA_DISABLED);
}

static esp_err_t measurement_device_add(sensor_t *s)
{
    /* S3 SPI2 exposes CS0..5, and spi_common.c supplies exactly that count
     * to the SDK bus lock. Half-duplex enables the documented CS pre-delay.
     * This is still FOUR separate protocol wires, not shared 3-wire data.
     * No HW dummy phase: SensorAPI includes and removes the one BMI dummy. */
    const spi_device_interface_config_t cfg = {
        .command_bits = 8, .address_bits = 0, .dummy_bits = 0,
        .mode = 0,
        .clock_source = SPI_CLK_SRC_DEFAULT,
        .clock_speed_hz = SPI_HZ,
        .cs_ena_pretrans = 1, .cs_ena_posttrans = 1,
        .spics_io_num = s->cs,
        .flags = SPI_DEVICE_HALFDUPLEX | SPI_DEVICE_NO_DUMMY,
        .queue_size = 1
    };
    esp_err_t err = spi_bus_add_device(MEASUREMENT_HOST, &cfg, &s->spi);
    if (err == ESP_OK) {
        err = spi_device_get_actual_freq(s->spi, &s->spi_khz);
    }
    if (err == ESP_OK && s->spi_khz != SPI_HZ / 1000) {
        err = ESP_ERR_INVALID_STATE;
    }
    return err;
}

/* The address's read/write bit is ALREADY prepared by bmi2_get/set_regs.
 * Reads receive len bytes INCLUDING the dummy. Writes send exactly len
 * data bytes. The separate 8-bit command is held under the SAME HW CS.
 * No silent cast of esp_err_t to Bosch's 8-bit return type. */
static BMI2_INTF_RETURN_TYPE sensor_transfer(sensor_t *s, uint8_t reg,
                                             uint8_t *read_data,
                                             const uint8_t *write_data,
                                             uint32_t len)
{
    if (s == NULL) {
        return BMI2_E_COM_FAIL;
    }
    if (s->spi == NULL || s->pending || len == 0 || len > SPI_DATA_LIMIT ||
        ((read_data == NULL) == (write_data == NULL))) {
        s->bus_error = ESP_ERR_INVALID_STATE;
        return BMI2_E_COM_FAIL;
    }
    memset(&s->transaction, 0, sizeof(s->transaction));
    s->transaction.cmd = reg;
    if (read_data != NULL) {
        s->transaction.rxlength = len * 8;
        s->transaction.rx_buffer = s->rx;
    } else {
        memcpy(s->tx, write_data, len);
        s->transaction.length = len * 8;
        s->transaction.tx_buffer = s->tx;
    }
    s->bus_error = spi_device_queue_trans(s->spi, &s->transaction,
                                         pdMS_TO_TICKS(SPI_TIMEOUT_MS));
    if (s->bus_error != ESP_OK) {
        return BMI2_E_COM_FAIL;
    }
    s->pending = true;
    spi_transaction_t *completed = NULL;
    s->bus_error = spi_device_get_trans_result(s->spi, &completed,
                                              pdMS_TO_TICKS(SPI_TIMEOUT_MS));
    if (s->bus_error != ESP_OK) {
        /* Do not free/reuse a potentially live transaction. This device
         * will be invalidated. A genuinely stuck shared bus can affect
         * others too; their own failures remain independently reported. */
        return BMI2_E_COM_FAIL;
    }
    if (completed != &s->transaction) {
        s->bus_error = ESP_ERR_INVALID_STATE;
        return BMI2_E_COM_FAIL;
    }
    s->pending = false;
    if (read_data != NULL) {
        memcpy(read_data, s->rx, len);
    }
    return BMI2_INTF_RET_SUCCESS;
}

static BMI2_INTF_RETURN_TYPE sensor_read(uint8_t reg, uint8_t *data,
                                         uint32_t len, void *intf_ptr)
{
    return sensor_transfer(intf_ptr, reg, data, NULL, len);
}

static BMI2_INTF_RETURN_TYPE sensor_write(uint8_t reg, const uint8_t *data,
                                          uint32_t len, void *intf_ptr)
{
    return sensor_transfer(intf_ptr, reg, NULL, data, len);
}

static esp_err_t measurement_uart_init(void)
{
    const uart_config_t uart = {
        .baud_rate = 115200,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_APB
    };
    esp_err_t err = uart_param_config(UART_NUM_0, &uart);
    if (err == ESP_OK) {
        err = uart_set_pin(UART_NUM_0, REV5_PIN_UART0_TX_GPIO,
                           REV5_PIN_UART0_RX_GPIO, UART_PIN_NO_CHANGE,
                           UART_PIN_NO_CHANGE);
    }
    if (err == ESP_OK) {
        /* No TX ring buffer: uart_tx_chars is explicitly nonblocking.
         * RX has a bounded driver buffer but no parser or command task. */
        err = uart_driver_install(UART_NUM_0, 256, 0, 0, NULL, 0);
    }
    return err;
}

static void saturating_increment(uint32_t *value)
{
    if (*value != UINT32_MAX) {
        ++*value;
    }
}

static bool uart_send_bounded(const char *data, size_t len)
{
    const int64_t deadline = esp_timer_get_time() + LOG_TIMEOUT_US;
    size_t sent = 0;
    while (sent < len && esp_timer_get_time() < deadline) {
        int n = uart_tx_chars(UART_NUM_0, data + sent, (uint32_t)(len - sent));
        if (n < 0) {
            return false;
        }
        sent += (size_t)n;
        if (sent < len) {
            vTaskDelay(1);
        }
    }
    return sent == len;
}

/* One application log producer, no unbounded queue. Truncated JSON is
 * never passed off as a complete sample. A partial TX is delimited before
 * the next record, and the cumulative drop count is in every next line. */
static void emit(const sensor_t *s, const char *kind, const char *status,
                 const char *reason, const char *extra)
{
    if (log_sequence == UINT64_MAX) {
        return; /* Never reuse a sequence number within this boot. */
    }
    char line[LOG_LINE_LIMIT + 1];
    const int count = snprintf(
        line, sizeof(line),
        "REV5B1 {\"kind\":\"%s\",\"boot_epoch\":null,\"seq\":%" PRIu64
        ",\"t_us\":%" PRIi64 ",\"sensor\":\"%s\",\"ref\":\"%s\""
        ",\"status\":\"%s\",\"reason\":\"%s\",\"api_rc\":%d,\"bus_rc\":%d"
        ",\"drop_total\":%" PRIu32 ",\"overrun_total\":%" PRIu32
        ",\"profile\":\"" PROFILE_ID "\",\"timing\":\"UNQUALIFIED\"%s}\n",
        kind, log_sequence++, esp_timer_get_time(),
        s ? s->identity->id : "ALL", s ? s->identity->sensor_ref : "U201",
        status, reason, s ? s->api_error : 0, s ? (int)s->bus_error : 0,
        dropped_lines, overrun_count, extra);
    if (count < 0 || count > LOG_LINE_LIMIT) {
        saturating_increment(&dropped_lines);
        return;
    }
    if (uart_needs_lf && !uart_send_bounded("\n", 1)) {
        saturating_increment(&dropped_lines);
        return;
    }
    uart_needs_lf = false;
    if (!uart_send_bounded(line, (size_t)count)) {
        uart_needs_lf = true;
        saturating_increment(&dropped_lines);
    }
}

static void fail_sensor(sensor_t *s, const char *reason, int8_t rc)
{
    /* Invalidate before logging: transport progress is not a prerequisite
     * for disabling this software producer. No motor state is affected. */
    s->ready = false;
    s->failure = reason;
    s->api_error = rc;
    char chip[8] = "null", internal[8] = "null", extra[96];
    if (s->chip_observed) {
        snprintf(chip, sizeof(chip), "%u", s->chip);
    }
    if (s->internal_observed) {
        snprintf(internal, sizeof(internal), "%u", s->internal);
    }
    snprintf(extra, sizeof(extra),
             ",\"raw\":null,\"last_chip_id\":%s,\"last_internal\":%s", chip, internal);
    emit(s, "IMU_ERROR", "INVALID", reason, extra);
}

static bool profile_matches(const struct bmi2_sens_config cfg[2])
{
    return cfg[0].cfg.acc.odr == BMI2_ACC_ODR_100HZ &&
           cfg[0].cfg.acc.range == BMI2_ACC_RANGE_2G &&
           cfg[0].cfg.acc.bwp == BMI2_ACC_NORMAL_AVG4 &&
           cfg[0].cfg.acc.filter_perf == BMI2_PERF_OPT_MODE &&
           cfg[1].cfg.gyr.odr == BMI2_GYR_ODR_100HZ &&
           cfg[1].cfg.gyr.range == BMI2_GYR_RANGE_2000 &&
           cfg[1].cfg.gyr.bwp == BMI2_GYR_NORMAL_MODE &&
           cfg[1].cfg.gyr.filter_perf == BMI2_PERF_OPT_MODE &&
           cfg[1].cfg.gyr.noise_perf == BMI2_PERF_OPT_MODE;
}

/* Runtime health rejects loss of chip/config/power-control state. This is
 * SPI register consistency, NOT a power-good input or physical guarantee. */
static int8_t read_health(sensor_t *s)
{
    uint8_t chip, internal, power, aps;
    int8_t rc = bmi2_get_regs(BMI2_CHIP_ID_ADDR, &chip, 1, &s->dev);
    if (rc != BMI2_OK) {
        return rc;
    }
    s->chip = chip;
    s->chip_observed = true;
    if (chip != BMI270_CHIP_ID) {
        return BMI2_E_DEV_NOT_FOUND;
    }
    rc = bmi2_get_regs(BMI2_INTERNAL_STATUS_ADDR, &internal, 1, &s->dev);
    if (rc != BMI2_OK) {
        return rc;
    }
    s->internal = internal;
    s->internal_observed = true;
    if ((internal & BMI2_CONFIG_LOAD_STATUS_MASK) != BMI2_CONFIG_LOAD_SUCCESS) {
        return BMI2_E_CONFIG_LOAD;
    }
    rc = bmi2_get_regs(BMI2_PWR_CTRL_ADDR, &power, 1, &s->dev);
    if (rc != BMI2_OK) {
        return rc;
    }
    if ((power & (BMI2_ACC_EN_MASK | BMI2_GYR_EN_MASK |
                  BMI2_AUX_EN_MASK | BMI2_TEMP_EN_MASK)) !=
                 (BMI2_ACC_EN_MASK | BMI2_GYR_EN_MASK)) {
        return BMI2_E_INVALID_STATUS;
    }
    rc = bmi2_get_adv_power_save(&aps, &s->dev);
    if (rc == BMI2_OK && aps != BMI2_DISABLE) {
        return BMI2_E_INVALID_STATUS;
    }
    return rc;
}

static int8_t read_profile(sensor_t *s)
{
    struct bmi2_sens_config cfg[2] = {
        { .type = BMI2_ACCEL }, { .type = BMI2_GYRO }
    };
    /* FW5-M1-001: Bosch v2.86.1 bmi270.c:1503-1636 (DS-IMU-085)
     * overwrites an earlier main-sensor error in multi-element get/set.
     * Use one element and check it before any later successful transfer
     * can erase that error. The initial get and set below do the same. */
    int8_t rc = bmi270_get_sensor_config(&cfg[0], 1, &s->dev);
    if (rc == BMI2_OK) {
        rc = bmi270_get_sensor_config(&cfg[1], 1, &s->dev);
    }
    if (rc == BMI2_OK && !profile_matches(cfg)) {
        rc = BMI2_E_INVALID_STATUS;
    }
    return rc;
}

static void initialize_sensor(sensor_t *s)
{
    s->dev = (struct bmi2_dev) {
        .intf = BMI2_SPI_INTF,
        .read = sensor_read,
        .write = sensor_write,
        .delay_us = sensor_delay_us,
        .read_write_len = CONFIG_CHUNK_BYTES,
        .intf_ptr = s
    };
    /* DS-IMU-079..084/088, exact Bosch bmi270_init -> bmi2_sec_init ->
     * bmi2_soft_reset -> bmi2_write_config_file. Do not shorten that path.
     * Initial and post-reset dummy reads each get the driver's 450 us APS
     * delay, exceeding the distinct 200 us SPI-selection interval. */
    int8_t rc = bmi270_init(&s->dev);
    if (rc != BMI2_OK) {
        if (rc == BMI2_E_DEV_NOT_FOUND) {
            /* On mismatch only, Bosch explicitly saves the observed ID. */
            s->chip = s->dev.chip_id;
            s->chip_observed = true;
        }
        fail_sensor(s, "BMI270_INIT", rc);
        return;
    }
    /* An additional post-upload identity/status check, not an abbreviated
     * substitute for the mandatory load/status checks inside Bosch init. */
    uint8_t chip, internal;
    rc = bmi2_get_regs(BMI2_CHIP_ID_ADDR, &chip, 1, &s->dev);
    if (rc == BMI2_OK) {
        s->chip = chip;
        s->chip_observed = true;
        if (chip != BMI270_CHIP_ID) {
            rc = BMI2_E_DEV_NOT_FOUND;
        }
    }
    if (rc == BMI2_OK) {
        rc = bmi2_get_internal_status(&internal, &s->dev);
        if (rc == BMI2_OK) {
            s->internal = internal;
            s->internal_observed = true;
            if ((internal & BMI2_CONFIG_LOAD_STATUS_MASK) != BMI2_CONFIG_LOAD_SUCCESS) {
                rc = BMI2_E_CONFIG_LOAD;
            }
        }
    }
    if (rc != BMI2_OK) {
        fail_sensor(s, "POST_INIT_ID_STATUS", rc);
        return;
    }
    rc = bmi2_set_adv_power_save(BMI2_DISABLE, &s->dev);
    if (rc != BMI2_OK) {
        fail_sensor(s, "DISABLE_APS", rc);
        return;
    }
    struct bmi2_sens_config cfg[2] = {
        { .type = BMI2_ACCEL }, { .type = BMI2_GYRO }
    };
    /* Read initial fields rather than inventing an OIS range image. OIS
     * itself stays disabled; only the named measurement fields change. */
    rc = bmi270_get_sensor_config(&cfg[0], 1, &s->dev);
    if (rc == BMI2_OK) {
        rc = bmi270_get_sensor_config(&cfg[1], 1, &s->dev);
    }
    if (rc != BMI2_OK) {
        fail_sensor(s, "READ_INITIAL_PROFILE", rc);
        return;
    }
    cfg[0].cfg.acc.odr = BMI2_ACC_ODR_100HZ;
    cfg[0].cfg.acc.range = BMI2_ACC_RANGE_2G;
    cfg[0].cfg.acc.bwp = BMI2_ACC_NORMAL_AVG4;
    cfg[0].cfg.acc.filter_perf = BMI2_PERF_OPT_MODE;
    cfg[1].cfg.gyr.odr = BMI2_GYR_ODR_100HZ;
    cfg[1].cfg.gyr.range = BMI2_GYR_RANGE_2000;
    cfg[1].cfg.gyr.bwp = BMI2_GYR_NORMAL_MODE;
    cfg[1].cfg.gyr.filter_perf = BMI2_PERF_OPT_MODE;
    cfg[1].cfg.gyr.noise_perf = BMI2_PERF_OPT_MODE;
    rc = bmi270_set_sensor_config(&cfg[0], 1, &s->dev);
    if (rc == BMI2_OK) {
        rc = bmi270_set_sensor_config(&cfg[1], 1, &s->dev);
    }
    if (rc == BMI2_OK) {
        rc = read_profile(s);
    }
    if (rc != BMI2_OK) {
        fail_sensor(s, "PROFILE_SET_READBACK", rc);
        return;
    }
    const uint8_t unused[] = { BMI2_AUX, BMI2_TEMP };
    const uint8_t enabled[] = { BMI2_ACCEL, BMI2_GYRO };
    rc = bmi270_sensor_disable(unused, ARRAY_COUNT(unused), &s->dev);
    if (rc == BMI2_OK) {
        rc = bmi270_sensor_enable(enabled, ARRAY_COUNT(enabled), &s->dev);
    }
    if (rc == BMI2_OK) {
        rc = read_health(s);
    }
    if (rc != BMI2_OK) {
        fail_sensor(s, "SENSOR_ENABLE_READBACK", rc);
        return;
    }
    s->ready = true;
    s->api_error = BMI2_OK;
    char extra[128];
    snprintf(extra, sizeof(extra),
             ",\"chip_id\":%u,\"internal\":%u,\"spi_khz\":%d,\"ready\":true",
             s->chip, s->internal, s->spi_khz);
    emit(s, "IMU_INIT", "UNQUALIFIED", "CONFIG_OK_PHYSICAL_TIMING_UNQUALIFIED", extra);
}

/* DS-IMU-087 and official bmi2.c get_acc_gyr_data: LSB,MSB signed 16-bit.
 * Explicit arithmetic avoids implementation-defined unsigned->int16 casts.
 * Deliberately NOT bmi2_get_sensor_data: that API applies cross-axis gyro
 * compensation and axis remapping, outside raw uncorrected bring-up. */
static int raw_signed_count(const uint8_t *bytes)
{
    const uint16_t word = (uint16_t)bytes[0] | ((uint16_t)bytes[1] << 8);
    return (word & UINT16_C(0x8000)) ? (int)word - 65536 : (int)word;
}

static void report_sample(sensor_t *s)
{
    if (!s->ready) {
        emit(s, "IMU_STATE", "UNAVAILABLE", s->failure, ",\"raw\":null");
        return;
    }
    int8_t rc = read_health(s);
    if (rc == BMI2_OK) {
        rc = read_profile(s);
    }
    if (rc != BMI2_OK) {
        fail_sensor(s, "HEALTH_OR_PROFILE_LOST", rc);
        return;
    }
    uint8_t status;
    rc = bmi2_get_status(&status, &s->dev);
    if (rc != BMI2_OK) {
        fail_sensor(s, "DRDY_BUS_READ", rc);
        return;
    }
    if ((status & (BMI2_DRDY_ACC | BMI2_DRDY_GYR)) !=
                  (BMI2_DRDY_ACC | BMI2_DRDY_GYR)) {
        emit(s, "IMU_STATE", "UNAVAILABLE", "ACC_GYR_NOT_READY", ",\"raw\":null");
        return;
    }
    uint8_t raw[12];
    const int64_t begin = esp_timer_get_time();
    rc = bmi2_get_regs(BMI2_ACC_X_LSB_ADDR, raw, sizeof(raw), &s->dev);
    const int64_t end = esp_timer_get_time();
    if (rc == BMI2_OK) {
        rc = read_health(s);
    }
    if (rc != BMI2_OK) {
        fail_sensor(s, "RAW_READ_OR_POST_HEALTH", rc);
        return;
    }
    char extra[192];
    const int count = snprintf(extra, sizeof(extra),
             ",\"t_begin_us\":%" PRIi64 ",\"t_end_us\":%" PRIi64
             ",\"raw\":[%d,%d,%d,%d,%d,%d]",
             begin, end, raw_signed_count(raw), raw_signed_count(raw + 2),
             raw_signed_count(raw + 4), raw_signed_count(raw + 6),
             raw_signed_count(raw + 8), raw_signed_count(raw + 10));
    if (count < 0 || (size_t)count >= sizeof(extra)) {
        saturating_increment(&dropped_lines);
        return;
    }
    s->api_error = BMI2_OK;
    emit(s, "IMU_RAW", "VALID_RAW", "", extra);
}

void app_main(void)
{
    /* SDK fixes clocks before app_main. Boot/default console is also
     * UART0; if driver creation fails ESP_ERROR_CHECK reports that failure
     * there. An unusable UART cannot guarantee host receipt of any error. */
    ESP_ERROR_CHECK(measurement_uart_init());
    emit(NULL, "BOOT", "UNQUALIFIED", "MEASUREMENT_ONLY_NO_RAIL_SENSE",
         ",\"commands\":false,\"boot_epoch_unique\":false");
    for (size_t i = 0; i < SENSOR_COUNT; ++i) {
        sensors[i].identity = &rev5_preparation_imus[i];
        sensors[i].cs = cs_pins[i];
        sensors[i].failure = "NOT_INITIALIZED";
    }
    esp_err_t err = select_all_spi_quiescent();
    if (err == ESP_OK) {
        err = measurement_bus_init();
    }
    if (err != ESP_OK) {
        for (size_t i = 0; i < SENSOR_COUNT; ++i) {
            sensors[i].bus_error = err;
            fail_sensor(&sensors[i], "GPIO_OR_SHARED_BUS_INIT", BMI2_E_COM_FAIL);
        }
        return; /* No clocked traffic after failed all-CS selection. */
    }
    /* Register all six CS slots before any SensorAPI transaction. */
    for (size_t i = 0; i < SENSOR_COUNT; ++i) {
        sensor_t *s = &sensors[i];
        s->bus_error = measurement_device_add(s);
        if (s->bus_error != ESP_OK) {
            fail_sensor(s, "SPI_DEVICE_ADD_OR_CLOCK", BMI2_E_COM_FAIL);
        }
    }
    for (size_t i = 0; i < SENSOR_COUNT; ++i) {
        if (sensors[i].spi != NULL && sensors[i].bus_error == ESP_OK) {
            initialize_sensor(&sensors[i]);
        }
    }
    for (;;) {
        const int64_t start = esp_timer_get_time();
        for (size_t i = 0; i < SENSOR_COUNT; ++i) {
            report_sample(&sensors[i]);
        }
        const int64_t elapsed = esp_timer_get_time() - start;
        if (elapsed < SCAN_PERIOD_US) {
            sensor_delay_us((uint32_t)(SCAN_PERIOD_US - elapsed), NULL);
        } else {
            saturating_increment(&overrun_count);
            vTaskDelay(1); /* No catch-up burst and no starvation. */
        }
    }
}
