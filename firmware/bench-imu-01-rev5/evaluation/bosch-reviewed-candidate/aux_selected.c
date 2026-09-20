/* Public Aux APIs only. Register constants/types come from unchanged Bosch headers.
 * Fake callbacks/delays are not hardware or whole-Aux qualification. */
#include "bmi270.h"
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(expr) do { if (!(expr)) { \
    fprintf(stderr, "FAIL %s line %d: %s\n", current_id, __LINE__, #expr); exit(2); \
} } while (0)
#define GUARD 16u
#define SENTINEL 0xa5
#define IO_LIMIT 200000u

static char current_id[128];
typedef struct {
    unsigned read, spi, aps, length, start, burst, mode, fault, at, busy;
} input_t;
typedef struct {
    input_t input;
    struct bmi2_dev dev;
    unsigned io, after_fault, fault_at, delays, delay_2, delay_450, delay_1000, delay_10000;
    unsigned position, transaction, data_attempts, address_attempts, status_attempts, polls;
    unsigned power_reads, power_writes, phase;
    uint8_t power;
    uint64_t delay_us, digest;
} aux_model_t;
static aux_model_t m;

static uint8_t pattern(unsigned index)
{
    return (uint8_t)((index * 37u) ^ (index >> 8) ^ (index >> 3) ^ 0x5au);
}

static void event(char operation, uint8_t address, uint32_t length)
{
    CHECK(++m.io <= IO_LIMIT);
    if (m.fault_at) {
        ++m.after_fault;
    }
    m.digest = (m.digest ^ (unsigned char)operation) * UINT64_C(1099511628211);
    m.digest = (m.digest ^ address) * UINT64_C(1099511628211);
    m.digest = (m.digest ^ length) * UINT64_C(1099511628211);
}

static BMI2_INTF_RETURN_TYPE fail(void)
{
    CHECK(!m.fault_at);
    m.fault_at = m.io;
    return -7; /* Non-success callback value; the public API maps it to COM_FAIL. */
}

static bool fault(unsigned operation)
{
    return !m.fault_at && m.input.mode == 1 && m.input.fault == operation &&
           m.input.at == m.transaction &&
           (operation != 2 || m.polls > m.input.busy);
}

static void delay(uint32_t period, void *context)
{
    CHECK(context == &m);
    ++m.delays;
    m.delay_us += period;
    switch (period) {
        case 2: ++m.delay_2; break;
        case 450: ++m.delay_450; break;
        case 1000: ++m.delay_1000; break;
        case 10000: ++m.delay_10000; break;
        default: CHECK(false);
    }
}

static BMI2_INTF_RETURN_TYPE read_regs(uint8_t address, uint8_t *data, uint32_t length, void *context)
{
    CHECK(context == &m && data != NULL);
    const unsigned dummy = m.input.spi ? 1 : 0;
    const uint8_t reg = address & BMI2_SPI_WR_MASK;
    CHECK(address == (uint8_t)(reg | (m.input.spi ? BMI2_SPI_RD_MASK : 0)));
    event('R', address, length);
    CHECK(length >= dummy && length <= 9);
    memset(data, 0, length);
    if (reg == BMI2_PWR_CONF_ADDR) {
        CHECK(length == 1 + dummy);
        const unsigned operation = m.power_reads++ ? 2 : 0;
        if (m.input.mode == 4 && m.input.fault == operation) {
            return fail();
        }
        data[dummy] = m.power;
    } else if (reg == BMI2_STATUS_ADDR) {
        CHECK(length == 1 + dummy && m.phase == (m.input.read ? 0u : 1u));
        ++m.status_attempts;
        ++m.polls;
        if (fault(2)) {
            return fail();
        }
        const bool busy = m.polls <= m.input.busy;
        data[dummy] = busy ? BMI2_AUX_BUSY : 0;
        if (!busy) {
            m.phase = 2;
        }
    } else {
        CHECK(m.input.read && reg == BMI2_AUX_X_LSB_ADDR && m.phase == 3);
        CHECK(length == m.input.burst + dummy && m.position < m.input.length);
        ++m.data_attempts;
        if (fault(1)) {
            return fail();
        }
        for (unsigned i = 0; i < m.input.burst; ++i) {
            data[dummy + i] = pattern(m.position + i);
        }
        const unsigned remaining = m.input.length - m.position;
        m.position += remaining < m.input.burst ? remaining : m.input.burst;
        ++m.transaction;
        m.polls = m.phase = 0;
    }
    return BMI2_INTF_RET_SUCCESS;
}

static BMI2_INTF_RETURN_TYPE write_regs(uint8_t address, const uint8_t *data,
                                       uint32_t length, void *context)
{
    CHECK(context == &m && data != NULL && length == 1);
    CHECK(!(address & BMI2_SPI_RD_MASK));
    event('W', address, length);
    m.digest = (m.digest ^ data[0]) * UINT64_C(1099511628211);
    if (address == BMI2_PWR_CONF_ADDR) {
        const unsigned operation = m.power_writes++ ? 3 : 1;
        if (m.input.mode == 4 && m.input.fault == operation) {
            return fail();
        }
        m.power = data[0];
    } else if (address == BMI2_AUX_WR_DATA_ADDR) {
        CHECK(!m.input.read && m.phase == 0 && m.position < m.input.length);
        CHECK(data[0] == pattern(m.position));
        ++m.data_attempts;
        if (fault(1)) {
            return fail();
        }
        m.phase = 1;
    } else {
        CHECK(address == (m.input.read ? BMI2_AUX_RD_ADDR : BMI2_AUX_WR_ADDR) && m.phase == 2);
        CHECK(data[0] == (uint8_t)(m.input.start +
                                 (m.input.read ? m.transaction * m.input.burst : m.position)));
        ++m.address_attempts;
        if (fault(3)) {
            return fail();
        }
        if (m.input.read) {
            m.phase = 3;
        } else {
            ++m.position;
            ++m.transaction;
            m.polls = m.phase = 0;
        }
    }
    return BMI2_INTF_RET_SUCCESS;
}

static void run_case(input_t input)
{
    memset(&m, 0, sizeof(m));
    m.input = input;
    m.digest = UINT64_C(14695981039346656037);
    m.power = input.aps ? BMI2_ADV_POW_EN_MASK : 0;
    m.dev = (struct bmi2_dev){
        .intf = input.spi ? BMI2_SPI_INTF : BMI2_I2C_INTF,
        .read = read_regs, .write = write_regs, .delay_us = delay, .intf_ptr = &m,
        .read_write_len = 32, .dummy_byte = (uint8_t)input.spi,
        .aps_status = (uint8_t)input.aps, .aux_man_en = BMI2_ENABLE,
        .aux_man_rd_burst_len = input.burst == 8 ? BMI2_AUX_READ_LEN_3 : BMI2_AUX_READ_LEN_0
    };
    const size_t size = input.length ? input.length : 1;
    uint8_t *allocation = malloc(size + 2 * GUARD);
    CHECK(allocation != NULL);
    memset(allocation, SENTINEL, size + 2 * GUARD);
    uint8_t *buffer = allocation + GUARD;
    if (!input.read) {
        for (unsigned i = 0; i < input.length; ++i) {
            buffer[i] = pattern(i);
        }
        CHECK(pattern(0) != pattern(256));
    }
    struct bmi2_dev *device = &m.dev;
    uint8_t *argument = buffer;
    if (input.mode == 3) {
        switch (input.fault) {
            case 0: device = NULL; break;
            case 1: case 6: argument = NULL; break;
            case 2: m.dev.read = NULL; break;
            case 3: m.dev.write = NULL; break;
            case 4: m.dev.delay_us = NULL; break;
            case 5: m.dev.aux_man_en = BMI2_DISABLE; break;
            case 7: CHECK(input.read); m.dev.aux_man_rd_burst_len = 4; break;
            default: CHECK(false);
        }
    }
    const int8_t result = input.read ?
        bmi2_read_aux_man_mode((uint8_t)input.start, argument, (uint16_t)input.length, device) :
        bmi2_write_aux_man_mode((uint8_t)input.start, argument, (uint16_t)input.length, device);
    int8_t expected = BMI2_OK;
    if (input.mode == 1) {
        expected = BMI2_E_COM_FAIL;
        CHECK(m.fault_at && !m.after_fault);
        CHECK(m.position == (input.read ? input.at * input.burst : input.at));
        CHECK(m.power_writes == input.aps && m.dev.aps_status == BMI2_DISABLE);
        CHECK(m.delay_10000 == input.busy);
        if (input.read) {
            CHECK(m.status_attempts == input.at + 1 + input.busy);
            CHECK(m.address_attempts == input.at + (input.fault != 2));
            CHECK(m.data_attempts == input.at + (input.fault == 1));
        } else {
            CHECK(m.data_attempts == input.at + 1);
            CHECK(m.status_attempts == input.at + (input.fault != 1) + input.busy);
            CHECK(m.address_attempts == input.at + (input.fault == 3));
        }
    } else if (input.mode == 2 && input.busy == 21) {
        expected = BMI2_E_AUX_BUSY;
        CHECK(m.status_attempts == 21 && m.delay_10000 == 21);
        CHECK(!m.position && !m.address_attempts && !m.fault_at);
        CHECK(m.dev.aps_status == BMI2_DISABLE && m.power_writes == input.aps);
    } else if (input.mode == 3) {
        expected = input.fault == 5 || input.fault == 7 ? BMI2_E_AUX_INVALID_CFG : BMI2_E_NULL_PTR;
        const bool disabled_before_invalid_burst = input.fault == 7 && input.aps;
        CHECK(m.io == (disabled_before_invalid_burst ? 2u : 0u) && !m.position);
        CHECK(m.dev.aps_status == (disabled_before_invalid_burst ? 0u : input.aps));
    } else if (input.mode == 4) {
        expected = input.fault & 1 ? BMI2_E_SET_APS_FAIL : BMI2_E_COM_FAIL;
        CHECK(m.fault_at && !m.after_fault);
        CHECK(m.position == (input.fault >= 2 ? input.length : 0u));
        /* Existing set_regs updates the cached APS bit even on a failed write.
         * Record that limitation; this candidate does not redesign APS policy. */
        CHECK(m.dev.aps_status == (input.fault == 0 || input.fault == 3));
        CHECK((m.power & BMI2_ADV_POW_EN_MASK) == (input.fault < 2 ? BMI2_ADV_POW_EN_MASK : 0));
    } else {
        CHECK(m.position == input.length && !m.fault_at && !m.after_fault);
        CHECK(m.dev.aps_status == input.aps);
        CHECK(m.power_reads == 2 * input.aps && m.power_writes == 2 * input.aps);
        const unsigned transactions = input.read ? (input.length + input.burst - 1) / input.burst : input.length;
        CHECK(m.transaction == transactions && m.data_attempts == transactions &&
              m.address_attempts == transactions && m.status_attempts == transactions + input.busy);
        CHECK(m.io == 3 * transactions + input.busy + 4 * input.aps);
        CHECK(m.delay_1000 == 2 * transactions && m.delay_10000 == input.busy);
        CHECK(m.delay_450 == 2 * input.aps);
        CHECK(m.delay_2 == 3 * transactions + input.busy + 2 * input.aps);
        CHECK(m.delays == 5 * transactions + 2 * input.busy + 4 * input.aps);
    }
    CHECK(result == expected && !m.after_fault);
    for (unsigned i = 0; i < GUARD; ++i) {
        CHECK(allocation[i] == SENTINEL && allocation[GUARD + size + i] == SENTINEL);
    }
    for (unsigned i = 0; i < size; ++i) {
        const uint8_t wanted = input.read ?
            (i < m.position ? pattern(i) : SENTINEL) :
            (i < input.length ? pattern(i) : SENTINEL);
        CHECK(buffer[i] == wanted);
    }
    printf("{\"id\":\"%s\",\"api_rc\":%d,\"io_callbacks\":%u,\"delay_callbacks\":%u,"
           "\"fault_callback\":%u,\"callbacks_after_fault\":%u,\"completed_bytes\":%u,"
           "\"data_attempts\":%u,\"status_attempts\":%u,\"address_attempts\":%u,"
           "\"aps_cached\":%u,\"aps_register\":%u,\"fake_delay_us\":%llu,"
           "\"io_digest\":\"%016llx\",\"guards_intact\":true,\"passed\":true}\n",
           current_id, result, m.io, m.delays, m.fault_at, m.after_fault, m.position,
           m.data_attempts, m.status_attempts, m.address_attempts, m.dev.aps_status, m.power,
           (unsigned long long)m.delay_us, (unsigned long long)m.digest);
    fflush(stdout);
    free(allocation);
}

int main(int argc, char **argv)
{
    CHECK(argc == 2);
    FILE *input = fopen(argv[1], "r");
    CHECK(input != NULL);
    unsigned count = 0;
    input_t row;
    int fields;
    while ((fields = fscanf(input, "%127s %u %u %u %u %u %u %u %u %u %u",
                            current_id, &row.read, &row.spi, &row.aps, &row.length,
                            &row.start, &row.burst, &row.mode, &row.fault, &row.at, &row.busy)) != EOF) {
        CHECK(fields == 11);
        run_case(row);
        ++count;
    }
    CHECK(!ferror(input) && fclose(input) == 0);
    printf("{\"summary\":\"COMPLETE_SELECTED_AUTHOR_HOST_ONLY\",\"cases\":%u}\n", count);
    return 0;
}
