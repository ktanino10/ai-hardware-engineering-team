/*
 * drv10983.h -- TI DRV10983 (U5) commissioning/status driver for the Rev 3
 * Motor Driver subsystem, over I2C1 (PB6=SCL/PB7=SDA,
 * hardware/schematic/bench-imu-01-design.md Section 7.5.4).
 *
 * Scope boundary (Firmware Engineer, this cycle -- open-loop bench
 * characterization only, see .github/agents/firmware-engineer.agent.md):
 * this driver's job is (1) commissioning U5 into PWM speed-control mode via
 * a register-mode-only I2C write (never an EEPROM commit -- this board's
 * motor rail voltage can never reach the EEPROM-write precondition,
 * DS-MTR-073), and (2) reading back U5's own status/fault/speed registers
 * as raw facts. It deliberately does NOT:
 *   - command motor speed -- that happens by driving the SPEED pin's PWM
 *     duty cycle directly (tim1_pwm.c) and the DIR pin (motor.c), a
 *     completely separate physical path from this I2C bus;
 *   - decide overspeed/lock-fault POLICY (REQ-405/406) -- that decision
 *     logic lives in motor.c; this file only hands motor.c the raw
 *     register-level facts it needs to make that decision.
 */
#ifndef BENCH_IMU_01_DRV10983_H
#define BENCH_IMU_01_DRV10983_H

#include <stdint.h>

typedef enum
{
    DRV10983_OK = 0,
    DRV10983_ERR_I2C,    /* an I2C1 transaction failed (NACK/bus error/timeout) */
    DRV10983_ERR_VERIFY, /* SysOpt9 readback after commissioning did not match the written value */
} drv10983_status_t;

/* Status register (0x10) bit -- set when ANY of the six lock-detect
 * schemes (or the no-motor-detect check) has tripped; the specific cause
 * is in the FaultCode register below. DS-MTR-059. */
#define DRV10983_STATUS_MTRLCK (1u << 4)

/* FaultCode register (0x1E, read-only) bits -- the specific-cause detail
 * behind DRV10983_STATUS_MTRLCK above. DS-MTR-074. */
#define DRV10983_FAULT_LOCK0  (1u << 0) /* lock-detection current limit tripped */
#define DRV10983_FAULT_LOCK1  (1u << 1) /* abnormal speed */
#define DRV10983_FAULT_LOCK2  (1u << 2) /* abnormal Kt (BEMF constant) */
#define DRV10983_FAULT_FAULT3 (1u << 3) /* no motor detected */
#define DRV10983_FAULT_LOCK4  (1u << 4) /* stuck in open loop */
#define DRV10983_FAULT_LOCK5  (1u << 5) /* stuck in closed loop */

/* Runs U5's register-mode (never EEPROM-commit) commissioning sequence:
 * unlocks register writes (EECtrl.SIdata=1), writes SysOpt9 with
 * SpdCtrlMd=1 (PWM speed-control mode) and every other SysOpt9 field left
 * at its factory-default value, then reads SysOpt9 back to confirm the
 * write actually took effect. See drv10983.c for the exact bit-by-bit
 * derivation of the target value and why a readback-verify step exists.
 *
 * MUST be re-invoked by motor.c every time U6's SHDN transitions low-to-
 * high (i.e. every time the motor rail is freshly re-powered): U5 itself
 * loses all power whenever SHDN is low (U6 fully de-energizes the motor
 * rail per the schematic's own Section 7.5.3/REQ-403 fail-safe intent), so
 * U5 reloads its EEPROM defaults (SpdCtrlMd=0, analog mode) on its next
 * power-up and forgets any prior register-mode commissioning. This
 * function itself does not touch SHDN or track power-state transitions --
 * that sequencing responsibility belongs to motor.c.
 */
drv10983_status_t drv10983_commission(void);

/* Reads the raw Status register (0x10). Returns 0 on success, -1 on I2C
 * failure. Caller decodes bits with the DRV10983_STATUS_* macros above. */
int drv10983_read_status(uint8_t *status_reg);

/* Reads the raw FaultCode register (0x1E). Returns 0 on success, -1 on I2C
 * failure. Caller decodes bits with the DRV10983_FAULT_* macros above. */
int drv10983_read_fault_code(uint8_t *fault_reg);

/* Reads the raw 16-bit MotorSpeed1:MotorSpeed2 register pair via the
 * datasheet's mandated two-step ordered-read sequence (MSB register 0x11
 * first, then LSB register 0x12 -- NOT a single burst read; see
 * drv10983.c for why). Velocity(Hz) = result/10 (DS-MTR-075 Equation 8).
 * DIAGNOSTIC-ONLY: TI's own datasheet states this readback "is not
 * accurate and has up to 6% error" -- REQ-405's actual overspeed
 * enforcement uses tim3_fg_get_rpm() (the FG tachometer path), never this
 * register; this function exists only to populate a human-readable
 * diagnostic CSV field. Returns 0 on success, -1 on I2C failure. */
int drv10983_read_motor_speed_raw(uint16_t *speed_hz_x10);

#endif /* BENCH_IMU_01_DRV10983_H */
