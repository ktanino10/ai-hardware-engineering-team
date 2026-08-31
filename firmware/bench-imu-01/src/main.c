/*
 * main.c -- Bench-IMU-01 driver-level bring-up firmware.
 *
 * Rev <=2: reads BMI270 accelerometer + gyroscope samples over I2C2 at
 * >=100 Hz (REQ-001) and forwards them as CSV lines over the USART2 UART
 * header (REQ-106), blinks the PA5 status/heartbeat LED (REQ-003), and
 * reports the MCU's last reset cause once at boot (the REQ-004/SW1
 * reinterpretation -- see reset_reason.h).
 *
 * Rev 3 adds open-loop bring-up/characterization of the Motor Driver +
 * Reaction Wheel subsystem (U5 DRV10983 + M1 + U6 TPS26631PWPR) -- see
 * motor.h for its own full design rationale, REQ-405/406 safety-policy
 * details, and host command grammar. The IMU and motor subsystems are
 * DELIBERATELY kept functionally independent here, including at the
 * FAILURE-MODE level: Rev <=2 blocked forever (an infinite loop) if BMI270
 * init failed, which was harmless when the IMU was the only subsystem on
 * the board but would have silently prevented the motor subsystem from
 * ever coming up at all once it existed -- `bmi_ok` now gates only the
 * IMU-specific sampling branch below, so a BMI270 bring-up failure no
 * longer blocks anything else on the board. See
 * firmware/bench-imu-01/bench-imu-01-firmware-design.md for the full
 * design rationale and Evidence ID citations behind every decision in this
 * file and the drivers it calls.
 *
 * Deliberately NOT implemented (see .github/agents/firmware-engineer.agent.md
 * "Out of scope"): USB data/enumeration (REQ-105 -- this board's USB port is
 * power-only), any wireless (REQ-006), any control loop / attitude control /
 * sensor fusion / physical-unit conversion (Control Engineer territory, not
 * yet triggered), and -- per this bring-up pass's own hard scope fence --
 * any code path that reads the IMU and reacts by driving the motor, or
 * vice versa. The two subsystems below share only this MCU, this UART
 * link, and this superloop; they do not otherwise reference each other.
 */
#include "bmi270.h"
#include "clock.h"
#include "gpio.h"
#include "i2c1.h"
#include "i2c2.h"
#include "motor.h"
#include "reset_reason.h"
#include "systick.h"
#include "tim1_pwm.h"
#include "tim3_fg.h"
#include "usart2.h"

#define SAMPLE_PERIOD_MS  10u  /* 100 Hz, exactly meeting REQ-001's floor */
#define LED_BLINK_MS      500u /* 1 Hz heartbeat blink (REQ-003), used while the IMU is healthy */
#define LED_BLINK_FAST_MS 100u /* faster, distinct blink rate used only while !bmi_ok -- preserves Rev <=2's "alive but IMU degraded" visual signal for a bench operator, without an infinite loop blocking the (independent) motor subsystem the way Rev <=2 did */

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
    uint8_t bmi_ok;
    uint32_t next_sample_ms;
    uint32_t next_blink_ms;

    clock_init();
    gpio_init();
    usart2_init();
    systick_init();

    usart2_write_str("\r\nBench-IMU-01 firmware boot (Rev 3: + Motor Driver/Reaction Wheel bring-up)\r\n");
    reset_reason_report();

    /* --- IMU subsystem bring-up (I2C2, BMI270). --- */
    i2c2_init();
    bmi_status = bmi270_init();
    bmi_ok = (bmi_status == BMI270_OK) ? 1u : 0u;
    if (!bmi_ok)
    {
        report_bmi270_error(bmi_status);
        /* Rev <=2 looped forever here. That is deliberately NOT done
         * anymore: with a second, functionally-independent subsystem (Rev
         * 3's motor driver) now sharing this board, an IMU bring-up
         * failure must not be able to prevent the motor subsystem from
         * ever initializing. `bmi_ok` instead gates only the IMU-specific
         * sampling branch below; the LED heartbeat switches to a faster,
         * distinct blink rate so a bench operator keeps the same
         * "firmware alive, IMU degraded" visual signal the old permanent
         * fast-blink loop gave, without the availability cost. */
    }
    else
    {
        usart2_write_str("BMI270_INIT_OK\r\n");
        usart2_write_str("ax,ay,az,gx,gy,gz are raw signed 16-bit register counts, NOT physical units\r\n");
        usart2_write_str("millis_ms,ax,ay,az,gx,gy,gz\r\n");
    }

    /* --- Motor Driver + Reaction Wheel subsystem bring-up (Rev 3): I2C1
     * (U5 commissioning/status bus), TIM1 (SPEED PWM), TIM3 (FG tachometer
     * capture). Brought up UNCONDITIONALLY, independent of bmi_ok -- see
     * this file's own top comment and .github/agents/firmware-engineer
     * .agent.md's scope fence: the IMU and motor subsystems are
     * functionally independent and share only this board/UART/superloop.
     * motor_init() itself leaves the motor rail DISARMED (SHDN low) until
     * an explicit REARM host command arrives -- these calls bring up
     * peripherals only; nothing is energized yet. --- */
    i2c1_init();
    tim1_pwm_init();
    tim3_fg_init();
    motor_init();

    next_sample_ms = millis();
    next_blink_ms = millis();

    for (;;)
    {
        uint32_t now = millis();
        uint8_t rx_byte;

        if ((int32_t)(now - next_blink_ms) >= 0)
        {
            led_toggle();
            next_blink_ms += bmi_ok ? LED_BLINK_MS : LED_BLINK_FAST_MS;
        }

        if (bmi_ok && (int32_t)(now - next_sample_ms) >= 0)
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

        /* Motor subsystem: safety checks (REQ-405/406) + CSV telemetry.
         * Runs every superloop pass, unconditionally -- see motor.c's own
         * motor_tick(): the REQ-405/406 checks inside are never rate-limited
         * or skipped. */
        motor_tick(now);

        /* Drain all currently-available host command bytes for the motor
         * subsystem. usart2_read_byte() is non-blocking (returns 0
         * immediately if RXNE is clear); this is a plain polling read, the
         * same discipline already used for I2C1/I2C2 elsewhere in this
         * firmware, chosen deliberately over adding a second interrupt
         * source: unlike TIM3's FG capture (where polling was PROVEN
         * unreliable at speed -- see tim3_fg.h), a human operator typing
         * short bench commands at a UART terminal has no comparable
         * high-rate/missed-edge risk, and USART2's single-byte hardware
         * RX buffer means at most one byte could theoretically be lost if
         * two arrive back-to-back while this loop is elsewhere (e.g.
         * inside check_lock_faults()'s I2C1 poll) -- an accepted, disclosed
         * limitation (see bench-imu-01-firmware-design.md): worst case is
         * a desynced/garbled command line, recoverable by retyping it, and
         * REQ-405/406's own safety behavior does not depend on RX
         * reliability at all (only on the FG/status sensing paths, which
         * are unaffected). */
        while (usart2_read_byte(&rx_byte))
        {
            motor_handle_rx_byte(rx_byte);
        }
    }
}
