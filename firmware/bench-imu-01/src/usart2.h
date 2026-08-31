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
 * This driver is transmit-focused (this board only needs to *forward*
 * sensor samples to a host, REQ-001/REQ-106 -- there is no host-to-board
 * command protocol in this cycle's scope). RE is still enabled in case a
 * future revision adds a command channel, but nothing reads RXNE yet.
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

#endif /* BENCH_IMU_01_USART2_H */
