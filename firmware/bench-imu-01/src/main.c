/*
 * main.c -- Bench-IMU-01 driver-level bring-up firmware.
 *
 * Reads BMI270 accelerometer + gyroscope samples over I2C2 at >=100 Hz
 * (REQ-001) and forwards them as CSV lines over the USART2 UART header
 * (REQ-106), blinks the PA5 status/heartbeat LED (REQ-003), and reports the
 * MCU's last reset cause once at boot (the REQ-004/SW1 reinterpretation --
 * see reset_reason.h). See
 * firmware/bench-imu-01/bench-imu-01-firmware-design.md for the full
 * design rationale and Evidence ID citations behind every decision in this
 * file and the drivers it calls.
 *
 * Deliberately NOT implemented (see .github/agents/firmware-engineer.agent.md
 * "Out of scope"): USB data/enumeration (REQ-105 -- this board's USB port is
 * power-only), any wireless (REQ-006), any control loop / sensor fusion /
 * physical-unit conversion (Control Engineer territory, not yet triggered).
 */
#include "bmi270.h"
#include "clock.h"
#include "gpio.h"
#include "i2c2.h"
#include "reset_reason.h"
#include "systick.h"
#include "usart2.h"

#define SAMPLE_PERIOD_MS 10u  /* 100 Hz, exactly meeting REQ-001's floor */
#define LED_BLINK_MS     500u /* 1 Hz heartbeat blink (REQ-003) */

static void report_bmi270_error(bmi270_status_t status)
{
    switch (status)
    {
        case BMI270_ERR_CHIP_ID:
            usart2_write_str("BMI270_INIT_FAILED: unexpected CHIP_ID (check I2C2 wiring/address)\r\n");
            break;
        case BMI270_ERR_I2C:
            usart2_write_str("BMI270_INIT_FAILED: I2C2 transaction error (NACK/bus/timeout)\r\n");
            break;
        case BMI270_ERR_CONFIG_LOAD:
            usart2_write_str("BMI270_INIT_FAILED: configuration file did not report load success\r\n");
            break;
        default:
            break;
    }
}

int main(void)
{
    bmi270_status_t bmi_status;
    uint32_t next_sample_ms;
    uint32_t next_blink_ms;

    clock_init();
    gpio_init();
    usart2_init();
    systick_init();

    usart2_write_str("\r\nBench-IMU-01 firmware boot\r\n");
    reset_reason_report();

    i2c2_init();
    bmi_status = bmi270_init();
    if (bmi_status != BMI270_OK)
    {
        report_bmi270_error(bmi_status);
        /* No IMU communication possible -- keep blinking the heartbeat LED
         * fast (distinct from the normal 1 Hz pattern) so a bench operator
         * can tell "firmware is alive but the sensor didn't come up" apart
         * from "board is dead", then stop: there is nothing useful left to
         * poll or transmit. */
        for (;;)
        {
            led_toggle();
            delay_ms(100u);
        }
    }
    usart2_write_str("BMI270_INIT_OK\r\n");
    usart2_write_str("ax,ay,az,gx,gy,gz are raw signed 16-bit register counts, NOT physical units\r\n");
    usart2_write_str("millis_ms,ax,ay,az,gx,gy,gz\r\n");

    next_sample_ms = millis();
    next_blink_ms = millis();

    for (;;)
    {
        uint32_t now = millis();

        if ((int32_t)(now - next_blink_ms) >= 0)
        {
            led_toggle();
            next_blink_ms += LED_BLINK_MS;
        }

        if ((int32_t)(now - next_sample_ms) >= 0)
        {
            bmi270_sample_t sample;

            next_sample_ms += SAMPLE_PERIOD_MS;

            if (bmi270_read_sample(&sample) == 0)
            {
                usart2_write_u32(now);
                usart2_write_str(",");
                usart2_write_i32(sample.acc_x);
                usart2_write_str(",");
                usart2_write_i32(sample.acc_y);
                usart2_write_str(",");
                usart2_write_i32(sample.acc_z);
                usart2_write_str(",");
                usart2_write_i32(sample.gyr_x);
                usart2_write_str(",");
                usart2_write_i32(sample.gyr_y);
                usart2_write_str(",");
                usart2_write_i32(sample.gyr_z);
                usart2_write_str("\r\n");
            }
            else
            {
                usart2_write_str("I2C2_READ_ERROR\r\n");
            }
        }
    }
}
