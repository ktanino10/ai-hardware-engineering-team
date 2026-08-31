/*
 * reset_reason.h -- reports why the MCU last reset, using RCC_CSR's reset-
 * reason flags.
 *
 * This exists specifically to correctly serve REQ-004 ("manual reset
 * button"). The kickoff brief for this firmware assumed SW1 would be a GPIO
 * firmware could "read" -- re-reading the actual schematic
 * (hardware/schematic/bench-imu-01-design.md Section 4.3, confirmed again in
 * requirements/traceability-matrix.md's REQ-004 row) shows SW1 is wired
 * directly from NRST to GND, in parallel with the always-populated NRST
 * filter cap C5. Pressing SW1 causes a hardware MCU reset; there is no GPIO
 * pin for application firmware to poll. The closest legitimate,
 * firmware-observable behavior tied to REQ-004 is this: report, once at
 * boot, which reset source RCC_CSR recorded (the NRST pin -- i.e. SW1 or a
 * debugger -- vs. power-on vs. watchdog vs. software), then clear the flags
 * so the next reset's cause isn't confused with this one's.
 */
#ifndef BENCH_IMU_01_RESET_REASON_H
#define BENCH_IMU_01_RESET_REASON_H

/* Reads RCC_CSR, writes a human-readable line describing the reset cause(s)
 * over USART2 (usart2_init() must already have been called), then clears
 * the flags via RCC_CSR's RMVF bit so they don't persist into the next
 * report. Call once, early in main(), after usart2_init(). */
void reset_reason_report(void);

#endif /* BENCH_IMU_01_RESET_REASON_H */
