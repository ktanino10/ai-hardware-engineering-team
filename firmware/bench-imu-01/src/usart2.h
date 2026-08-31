/*
 * usart2.h -- USART2 driver for the J2 UART header (TX/RX/GND/3V3),
 * REQ-106. Host communication baud rate/framing (Firmware Engineer decision,
 * this cycle, since the schematic deliberately leaves the exact baud rate
 * open -- Section 6 only cites "115200" as an example of what the internal
 * HSI16 oscillator's tolerance can support):
 *
 *   115200 baud, 8 data bits, no parity, 1 stop bit (8N1) -- ubiquitous
 *   default for USB-serial adapters, needs no special host-side
 *   configuration, and matches the schematic's own example figure.
 *
 * REVALIDATED (Rev 3 motor subsystem, this cycle): this driver was
 * previously transmit-focused only ("no host-to-board command protocol in
 * this cycle's scope"). That is no longer true -- motor.c's open-loop
 * speed-setpoint/RPM-report characterization routine needs a host-to-board
 * command channel (SPD/DIR/STOP/REARM, see motor.h) to actually be usable
 * from a bench operator's terminal, and REQ-406's deliberate-re-arm
 * requirement is most naturally satisfied by a specific host command. RE
 * was already enabled in usart2_init() for exactly this eventuality; only a
 * non-blocking single-byte read function was missing, added below.
 * Line-buffering/command-parsing itself lives in motor.c, not here -- this
 * file's job stays "raw byte in, raw byte out", matching its existing
 * scope for TX.
 */
#ifndef BENCH_IMU_01_USART2_H
#define BENCH_IMU_01_USART2_H

#include <stdint.h>

void usart2_init(void);
void usart2_write_byte(uint8_t b);
void usart2_write_str(const char *s);

/* Writes an unsigned/signed decimal integer as ASCII, no leading zeros. */
void usart2_write_u32(uint32_t v);
void usart2_write_i32(int32_t v);

/* Non-blocking receive: if a byte has arrived (ISR.RXNE set), stores it in
 * *out and returns 1; otherwise returns 0 immediately without blocking.
 * Reading RDR (done only in the RXNE-set branch) clears RXNE itself, the
 * standard STM32 USART behaviour -- no separate ICR write needed. Intended
 * to be polled once per main-loop iteration (main.c), matching this
 * firmware's existing "polling, not interrupt-driven" philosophy for
 * non-timing-critical I/O (contrast tim3_fg.h's ISR, which exists because
 * FG capture genuinely cannot be safely polled -- a host command byte
 * arriving a superloop-iteration late has no safety consequence). */
int usart2_read_byte(uint8_t *out);

#endif /* BENCH_IMU_01_USART2_H */
