/*
 * Non-device callback model for actual public BMI270 initialization / FIFO / CRT.
 * Never reads a configuration span until its entire extent is checked.
 * This is not a silicon timing, calibration or security-exploit demonstration.
 */
#include "bmi270.h"
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef EXPECT_FIXED
#error "Build explicitly as original baseline or isolated candidate."
#endif

#define CHECK(expr) do { if (!(expr)) { \
    fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #expr); exit(2); \
} } while (0)
#define CONFIG_BYTES 8192u
#define CRT_START 6144u
#define CRT_END 8192u
#define CRT_BYTES (CRT_END - CRT_START)
#define MAX_REQUESTS 1100u
#define CALLBACK_LIMIT 30000u
#define STATE_CALLBACK_LIMIT 256u
#define MAX_STATE_EVENTS 1024u

enum fault { NONE, ADDRESS, DATA, TRIGGER, READY_READ, FIRST_FEATURE_READ };
enum state_path { NO_DOWNLOAD, BUSY, UNSUPPORTED, EARLY_FEATURE_ERROR };
typedef struct {
    unsigned offset, length, encoded_offset;
    bool accepted;
} request_t;
typedef struct {
    char operation;
    unsigned address, length, delay, caller_length;
    int result;
} event_t;
typedef struct {
    struct bmi2_dev dev;
    uint8_t regs[128], features[8][16], page;
    unsigned init_offset, init_bytes, init_requests;
    unsigned callbacks, fault_at, after_fault, budget_hits;
    unsigned requests, accepted_bytes, accepted_requests, unsafe_requests;
    unsigned ready_reads, triggers, first_unsafe_offset, first_unsafe_len, unsafe_excess;
    bool crt_phase, download_started, completion_pending, stuck_ready;
    enum fault fault;
    request_t spans[MAX_REQUESTS];
    bool trace_state;
    unsigned events, delays;
    event_t trace[MAX_STATE_EVENTS];
} model_t;
static model_t model;
static unsigned cases;

static bool callback_budget(model_t *m)
{
    ++m->callbacks;
    if (m->fault_at) {
        ++m->after_fault;
    }
    if (m->callbacks > (m->trace_state ? STATE_CALLBACK_LIMIT : CALLBACK_LIMIT)) {
        ++m->budget_hits;
        return false;
    }
    return true;
}

static BMI2_INTF_RETURN_TYPE inject(model_t *m)
{
    CHECK(!m->fault_at);
    m->fault_at = m->callbacks;
    return BMI2_E_COM_FAIL;
}

static BMI2_INTF_RETURN_TYPE read_registers_impl(uint8_t address, uint8_t *out,
                                                uint32_t length, void *context)
{
    model_t *m = context;
    if (!callback_budget(m)) {
        return BMI2_E_COM_FAIL;
    }
    const uint8_t reg = address & BMI2_SPI_WR_MASK;
    const unsigned dummy = m->dev.intf == BMI2_SPI_INTF ? 1u : 0u;
    CHECK(length >= dummy && length <= BMI2_MAX_LEN);
    if (m->crt_phase && m->fault == FIRST_FEATURE_READ &&
        reg == BMI2_FEATURES_REG_ADDR && !m->fault_at) {
        return inject(m);
    }
    if (m->crt_phase && m->fault == READY_READ && m->accepted_bytes &&
        reg == BMI2_GYR_CRT_CONF_ADDR && !m->fault_at) {
        return inject(m);
    }
    memset(out, 0, length);
    if (reg == BMI2_GYR_CRT_CONF_ADDR && m->completion_pending &&
        ++m->ready_reads >= 3) {
        m->regs[reg] &= (uint8_t)~BMI2_GYR_CRT_RUNNING_MASK;
    }
    for (unsigned i = dummy; i < length; ++i) {
        unsigned source = (unsigned)reg + i - dummy;
        CHECK(source < sizeof(m->regs));
        out[i] = source >= BMI2_FEATURES_REG_ADDR &&
                 source < BMI2_FEATURES_REG_ADDR + BMI2_FEAT_SIZE_IN_BYTES ?
                 m->features[m->page][source - BMI2_FEATURES_REG_ADDR] : m->regs[source];
    }
    return BMI2_INTF_RET_SUCCESS;
}

static BMI2_INTF_RETURN_TYPE write_registers_impl(uint8_t address, const uint8_t *data,
                                                 uint32_t length, void *context)
{
    model_t *m = context;
    if (!callback_budget(m)) {
        return BMI2_E_COM_FAIL;
    }
    const uint8_t reg = address & BMI2_SPI_WR_MASK;
    if (reg == BMI2_INIT_DATA_ADDR) {
        /* Convert pointers to integer addresses; no subtraction of unrelated
         * objects or access to bytes outside the declared real config array. */
        const uintptr_t begin = (uintptr_t)m->dev.config_file_ptr;
        const uintptr_t ptr = (uintptr_t)data;
        CHECK(begin && ptr >= begin && ptr - begin <= CONFIG_BYTES);
        const unsigned offset = (unsigned)(ptr - begin);
        const bool in_object = length <= CONFIG_BYTES - offset;
        const bool in_slice = !m->crt_phase ||
                              (offset >= CRT_START && offset <= CRT_END &&
                               length <= CRT_END - offset);
        if (m->crt_phase) {
            CHECK(m->requests < MAX_REQUESTS);
            request_t *span = &m->spans[m->requests++];
            *span = (request_t){offset, length, m->init_offset, false};
            if (!in_object || !in_slice) {
                ++m->unsafe_requests;
                m->first_unsafe_offset = offset;
                m->first_unsafe_len = length;
                m->unsafe_excess = offset + length > CRT_END ? offset + length - CRT_END : 0;
                /* Deliberately do not dereference or transmit this request. */
                return BMI2_E_COM_FAIL;
            }
            if (m->fault == DATA && m->requests == 2 && !m->fault_at) {
                return inject(m);
            }
            for (unsigned i = 0; i < length; ++i) {
                CHECK(data[i] == m->dev.config_file_ptr[offset + i]);
            }
            span->accepted = true;
            ++m->accepted_requests;
            m->accepted_bytes += length;
        } else {
            CHECK(in_object && offset == m->init_bytes && offset == m->init_offset);
            CHECK(!(offset & 1u) && !(length & 1u));
            for (unsigned i = 0; i < length; ++i) {
                CHECK(data[i] == m->dev.config_file_ptr[offset + i]);
            }
            m->init_bytes += length;
            ++m->init_requests;
        }
        return BMI2_INTF_RET_SUCCESS;
    }
    if (m->crt_phase && m->fault == ADDRESS && m->download_started &&
        reg == BMI2_INIT_ADDR_0 && m->accepted_requests == 1 && !m->fault_at) {
        return inject(m);
    }
    if (reg == BMI2_CMD_REG_ADDR && length == 1 && data[0] == BMI2_G_TRIGGER_CMD) {
        if (m->crt_phase && m->fault == TRIGGER && m->accepted_bytes && !m->fault_at) {
            return inject(m);
        }
        ++m->triggers;
        m->download_started = true;
        if (!m->stuck_ready) {
            m->regs[BMI2_GYR_CRT_CONF_ADDR] ^= BMI2_GYR_RDY_FOR_DL_MASK;
        }
        if (m->accepted_bytes >= CRT_BYTES ||
            m->features[BMI2_PAGE_1][BMI270_MAX_BURST_LEN_STRT_ADDR] == 0) {
            m->completion_pending = true;
            m->ready_reads = 0;
        }
    }
    if (reg == BMI2_CMD_REG_ADDR && length == 1 && data[0] == BMI2_SOFT_RESET_CMD) {
        memset(m->regs, 0, sizeof(m->regs));
        memset(m->features, 0, sizeof(m->features));
        m->regs[BMI2_CHIP_ID_ADDR] = BMI270_CHIP_ID;
        m->regs[BMI2_INTERNAL_STATUS_ADDR] = BMI2_CONFIG_LOAD_SUCCESS;
        m->regs[BMI2_PWR_CONF_ADDR] = BMI2_ADV_POW_EN_MASK;
        m->regs[BMI2_GYR_SELF_TEST_AXES_ADDR] = 0x0f;
        m->init_bytes = m->init_requests = 0;
    }
    CHECK(length && (unsigned)reg + length <= sizeof(m->regs));
    for (unsigned i = 0; i < length; ++i) {
        const unsigned destination = (unsigned)reg + i;
        if (destination >= BMI2_FEATURES_REG_ADDR &&
            destination < BMI2_FEATURES_REG_ADDR + BMI2_FEAT_SIZE_IN_BYTES) {
            m->features[m->page][destination - BMI2_FEATURES_REG_ADDR] = data[i];
        } else {
            m->regs[destination] = data[i];
        }
    }
    if (reg == BMI2_FEAT_PAGE_ADDR) {
        CHECK(length == 1 && data[0] < 8);
        m->page = data[0];
    }
    if (reg == BMI2_INIT_ADDR_0) {
        CHECK(length == 2);
        m->init_offset = (((unsigned)data[1] << 4) | (data[0] & 15u)) * 2u;
    }
    return BMI2_INTF_RET_SUCCESS;
}

static void trace_callback(model_t *m, char operation, uint8_t address, uint32_t length,
                           uint32_t delay, int result)
{
    if (m->trace_state) {
        CHECK(m->events < MAX_STATE_EVENTS);
        m->trace[m->events++] = (event_t){
            operation, address & BMI2_SPI_WR_MASK, length, delay,
            m->dev.read_write_len, result
        };
    }
}

static BMI2_INTF_RETURN_TYPE read_registers(uint8_t address, uint8_t *out,
                                           uint32_t length, void *context)
{
    const BMI2_INTF_RETURN_TYPE rc = read_registers_impl(address, out, length, context);
    trace_callback(context, 'R', address, length, 0, rc);
    return rc;
}

static BMI2_INTF_RETURN_TYPE write_registers(uint8_t address, const uint8_t *data,
                                            uint32_t length, void *context)
{
    const BMI2_INTF_RETURN_TYPE rc = write_registers_impl(address, data, length, context);
    trace_callback(context, 'W', address, length, 0, rc);
    return rc;
}

static void delay_us(uint32_t period, void *context)
{
    model_t *m = context;
    if (m->trace_state) {
        ++m->delays;
        trace_callback(m, 'D', 0, 0, period, 0);
    }
}

static void initialize(unsigned requested, bool fifo, enum bmi2_intf intf)
{
    memset(&model, 0, sizeof(model));
    model.regs[BMI2_CHIP_ID_ADDR] = BMI270_CHIP_ID;
    model.dev = (struct bmi2_dev){
        .intf = intf, .read = read_registers, .write = write_registers,
        .delay_us = delay_us, .read_write_len = (uint16_t)requested, .intf_ptr = &model
    };
    CHECK(bmi270_init(&model.dev) == BMI2_OK);
    CHECK(model.dev.config_size == CONFIG_BYTES && model.init_bytes == CONFIG_BYTES);
    CHECK(model.dev.read_write_len == (requested < 2 ? 2 : requested & ~1u));
    CHECK(model.dev.aps_status == BMI2_ENABLE);
    CHECK(bmi2_set_adv_power_save(BMI2_DISABLE, &model.dev) == BMI2_OK);
    if (fifo) {
        CHECK(bmi2_set_fifo_config(BMI2_FIFO_ACC_EN | BMI2_FIFO_GYR_EN, BMI2_ENABLE, &model.dev) == BMI2_OK);
        CHECK(model.features[BMI2_PAGE_1][BMI270_MAX_BURST_LEN_STRT_ADDR] != 0);
    }
    model.crt_phase = true;
}

static unsigned effective(unsigned value)
{
    return value < 2 ? 2 : (value > 510 ? 510 : value & ~1u);
}

static void complete_spans(unsigned chunk)
{
    unsigned cursor = CRT_START, full_end = CRT_END - CRT_BYTES % chunk;
    for (unsigned i = 0; i < model.requests; ++i) {
        request_t span = model.spans[i];
        const unsigned expected = cursor < full_end ? chunk : 2;
        CHECK(span.accepted && span.offset == cursor && span.encoded_offset == cursor);
        CHECK(span.length == expected && span.length <= CRT_END - cursor);
        CHECK(!(span.offset & 1u) && !(span.length & 1u));
        cursor += span.length;
    }
    CHECK(cursor == CRT_END && model.accepted_bytes == CRT_BYTES && !model.unsafe_requests);
    CHECK(model.requests == CRT_BYTES / chunk + (CRT_BYTES % chunk) / 2);
}

static void report(const char *name, unsigned requested, int8_t rc)
{
    ++cases;
    CHECK(!model.budget_hits);
    printf("{\"case\":\"%s\",\"fixed\":%s,\"requested\":%u,\"effective\":%u,"
           "\"api_rc\":%d,\"requests\":%u,\"accepted_bytes\":%u,\"unsafe_requests\":%u,"
           "\"unsafe_offset\":%u,\"unsafe_length\":%u,\"unsafe_excess\":%u,"
           "\"fault_callback\":%u,\"callbacks_after_fault\":%u,"
           "\"entry\":\"bmi270_init+bmi2_set_fifo_config+bmi2_do_crt_or_gyro_st\","
           "\"unsafe_bytes_read\":0,\"spans\":[",
           name, EXPECT_FIXED ? "true" : "false", requested, model.dev.read_write_len,
           rc, model.requests, model.accepted_bytes, model.unsafe_requests,
           model.first_unsafe_offset, model.first_unsafe_len, model.unsafe_excess,
           model.fault_at, model.after_fault);
    for (unsigned i = 0; i < model.requests; ++i) {
        const request_t span = model.spans[i];
        printf("%s[%u,%u,%u,%s]", i ? "," : "", span.offset, span.length,
               span.encoded_offset, span.accepted ? "true" : "false");
    }
    puts("]}");
}

static void valid_case(unsigned requested, bool gyro_self_test, enum bmi2_intf intf)
{
    initialize(32, true, intf);
    model.dev.read_write_len = (uint16_t)requested;
    int8_t rc = gyro_self_test ? bmi2_do_gyro_st(&model.dev) : bmi2_do_crt(&model.dev);
    bool unsafe = !EXPECT_FIXED && (requested == 448 || requested == 358 || requested == 19);
    if (unsafe) {
        CHECK(rc == BMI2_E_COM_FAIL && model.unsafe_requests == 1);
        const unsigned start = requested == 448 ? 7936 : requested == 358 ? 7934 : 8191;
        const unsigned length = requested == 19 ? 2 : requested;
        CHECK(model.first_unsafe_offset == start && model.first_unsafe_len == length);
        CHECK(model.unsafe_excess == (requested == 448 ? 192 : requested == 358 ? 100 : 1));
    } else {
        CHECK(rc == BMI2_OK);
        CHECK(model.dev.read_write_len == effective(requested));
        complete_spans(effective(requested));
        CHECK(model.features[BMI2_PAGE_1][BMI270_MAX_BURST_LEN_STRT_ADDR] == 0);
    }
    report(gyro_self_test ? "public_gyro_self_test" :
           intf == BMI2_I2C_INTF ? "public_CRT_I2C" : "public_CRT_SPI", requested, rc);
}

static int state_case(enum state_path path, unsigned requested, bool gyro)
{
    static const char *names[] = {"no_download", "busy", "unsupported", "early_feature_io_error"};
    const bool fifo = path == BUSY || path == UNSUPPORTED;
    initialize(32, fifo, BMI2_SPI_INTF);
    model.dev.read_write_len = (uint16_t)requested;
    if (path == BUSY) {
        model.regs[BMI2_GYR_CRT_CONF_ADDR] |= BMI2_GYR_CRT_RUNNING_MASK;
    } else if (path == UNSUPPORTED) {
        model.dev.variant_feature = 0;
    } else if (path == EARLY_FEATURE_ERROR) {
        model.fault = FIRST_FEATURE_READ;
    }
    const unsigned before = model.dev.read_write_len;
    const unsigned maxburst_before = model.features[BMI2_PAGE_1][BMI270_MAX_BURST_LEN_STRT_ADDR];
    model.callbacks = 0;
    model.trace_state = true;
    const int8_t rc = gyro ? bmi2_do_gyro_st(&model.dev) : bmi2_do_crt(&model.dev);
    const unsigned expected_length = EXPECT_FIXED && path != UNSUPPORTED ? effective(requested) : requested;
    const int8_t source_expected_rc = path == BUSY ? BMI2_E_ST_ALREADY_RUNNING :
                                     path == UNSUPPORTED ? BMI2_E_INVALID_SENSOR : BMI2_OK;
    bool observation_matches = rc == source_expected_rc &&
        model.dev.read_write_len == expected_length && !model.requests &&
        !model.unsafe_requests && !model.budget_hits;
    if (path == UNSUPPORTED) {
        observation_matches = observation_matches && !model.events && !model.callbacks && !model.triggers;
    } else {
        observation_matches = observation_matches && model.callbacks && model.events &&
            model.trace[0].caller_length == expected_length;
        if (path == BUSY) {
            const unsigned feature_reads = expected_length < BMI2_FEAT_SIZE_IN_BYTES ?
                                           BMI2_FEAT_SIZE_IN_BYTES / expected_length : 1;
            observation_matches = observation_matches && model.callbacks == feature_reads + 2 &&
                                  !model.triggers;
        } else {
            observation_matches = observation_matches && model.triggers == 1;
        }
    }
    if (path == EARLY_FEATURE_ERROR) {
        observation_matches = observation_matches && model.fault_at == 2 && model.after_fault > 0;
    } else {
        observation_matches = observation_matches && !model.fault_at;
    }
    const bool error_preserved = path != EARLY_FEATURE_ERROR ||
        (rc == BMI2_E_COM_FAIL && !model.after_fault && !model.triggers);
    printf("{\"case\":\"state_path\",\"path\":\"%s\",\"public_entry\":\"%s\","
           "\"fixed\":%s,\"interface\":\"SPI\",\"initialization_length\":32,"
           "\"fifo_setup\":%s,\"maxburst_before\":%u,\"requested\":%u,"
           "\"pre_length\":%u,\"post_length\":%u,\"first_callback_length\":",
           names[path], gyro ? "bmi2_do_gyro_st" : "bmi2_do_crt",
           EXPECT_FIXED ? "true" : "false", fifo ? "true" : "false",
           maxburst_before, requested, before, model.dev.read_write_len);
    if (model.events) {
        printf("%u", model.trace[0].caller_length);
    } else {
        printf("null");
    }
    printf(",\"api_rc\":%d,\"source_expected_rc\":%d,\"io_callbacks\":%u,"
           "\"delay_callbacks\":%u,\"fault_callback\":%u,\"callbacks_after_fault\":%u,"
           "\"trigger_commands\":%u,\"upload_requests\":%u,\"accepted_bytes\":%u,"
           "\"unsafe_requests\":%u,\"unsafe_bytes_read\":0,\"budget_hits\":%u,"
           "\"source_observation_matches\":%s,\"early_error_preserved\":%s,\"trace\":[",
           rc, source_expected_rc, model.callbacks, model.delays, model.fault_at, model.after_fault,
           model.triggers, model.requests, model.accepted_bytes, model.unsafe_requests, model.budget_hits,
           observation_matches ? "true" : "false", error_preserved ? "true" : "false");
    for (unsigned i = 0; i < model.events; ++i) {
        const event_t e = model.trace[i];
        printf("%s[\"%c\",%u,%u,%u,%u,%d]", i ? "," : "", e.operation,
               e.address, e.length, e.delay, e.caller_length, e.result);
    }
    puts("]}");
    fflush(stdout);
    ++cases;
    if (!observation_matches) {
        return 2;
    }
    /* A source-predicted swallowed I/O error is evidence, not a passing oracle. */
    return EXPECT_FIXED && !error_preserved ? 3 : 0;
}

static int state_paths(void)
{
    const unsigned lengths[] = {0, 1, 19, 512, 65535, 32};
    for (enum state_path path = NO_DOWNLOAD; path <= EARLY_FEATURE_ERROR; ++path) {
        for (unsigned gyro = 0; gyro < 2; ++gyro) {
            for (unsigned i = 0; i < sizeof(lengths) / sizeof(lengths[0]); ++i) {
                if (!EXPECT_FIXED && path != UNSUPPORTED && lengths[i] < 2) {
                    continue;
                }
                const int result = state_case(path, lengths[i], gyro != 0);
                if (result) {
                    printf("{\"summary\":\"%s\",\"cases\":%u,\"fixed\":%s,"
                           "\"remaining_cases_executed\":false}\n",
                           result == 3 ? "BLOCKED_CANDIDATE_EARLY_FEATURE_ERROR" : "FAILED_STATE_OBSERVATION",
                           cases, EXPECT_FIXED ? "true" : "false");
                    return result;
                }
            }
        }
    }
    printf("{\"summary\":\"COMPLETE_STATE_OBSERVATIONS_NOT_ACCEPTANCE\","
           "\"cases\":%u,\"fixed\":%s,\"private_helper_called\":false,\"physical_or_SDK_IO\":false}\n",
           cases, EXPECT_FIXED ? "true" : "false");
    return 0;
}

int main(int argc, char **argv)
{
    if (argc == 2 && strcmp(argv[1], "--state-paths") == 0) {
        return state_paths();
    }
    CHECK(argc == 1);
    const unsigned chunks[] = {32, 448, 358, 2, 510, 19};
    for (unsigned i = 0; i < sizeof(chunks) / sizeof(chunks[0]); ++i) {
        valid_case(chunks[i], false, BMI2_SPI_INTF);
    }
    valid_case(448, true, BMI2_SPI_INTF);
    valid_case(358, false, BMI2_I2C_INTF);
    valid_case(512, false, BMI2_SPI_INTF);
    valid_case(65535, false, BMI2_SPI_INTF);

    initialize(19, true, BMI2_SPI_INTF);
    CHECK(model.dev.read_write_len == 18);
    int8_t rc = bmi2_do_crt(&model.dev);
    CHECK(rc == BMI2_OK);
    complete_spans(18);
    report("pre_init_19_normalizes_to_18", 19, rc);

    for (unsigned initial = 0; initial < 2; ++initial) {
        initialize(initial, true, BMI2_SPI_INTF);
        CHECK(model.dev.read_write_len == 2);
        rc = bmi2_do_crt(&model.dev);
        CHECK(rc == BMI2_OK);
        complete_spans(2);
        report("pre_init_minimum_normalizes_to_2", initial, rc);
    }
    if (EXPECT_FIXED) {
        valid_case(0, false, BMI2_SPI_INTF);
        valid_case(1, false, BMI2_SPI_INTF);
    }

    for (enum fault f = ADDRESS; f <= READY_READ; ++f) {
        initialize(32, true, BMI2_SPI_INTF);
        model.fault = f;
        rc = bmi2_do_crt(&model.dev);
        CHECK(rc == BMI2_E_COM_FAIL && model.fault_at && !model.after_fault);
        CHECK(model.accepted_bytes < CRT_BYTES && !model.unsafe_requests);
        report("public_transfer_error_stops", f, rc);
    }

    initialize(32, true, BMI2_SPI_INTF);
    model.stuck_ready = true;
    rc = bmi2_do_crt(&model.dev);
    CHECK(rc == BMI2_E_CRT_READY_FOR_DL_FAIL_ABORT && !model.requests);
    report("public_download_ready_timeout", 32, rc);

    initialize(32, true, BMI2_SPI_INTF);
    model.regs[BMI2_GYR_CRT_CONF_ADDR] |= BMI2_GYR_CRT_RUNNING_MASK;
    rc = bmi2_do_crt(&model.dev);
    CHECK(rc == BMI2_E_ST_ALREADY_RUNNING && !model.requests);
    report("public_busy_error", 32, rc);

    initialize(32, false, BMI2_SPI_INTF);
    rc = bmi2_do_crt(&model.dev);
    CHECK(rc == BMI2_OK && !model.requests);
    report("public_zero_maxburst_no_download", 32, rc);

    initialize(32, true, BMI2_SPI_INTF);
    model.dev.variant_feature = 0;
    rc = bmi2_do_crt(&model.dev);
    CHECK(rc == BMI2_E_INVALID_SENSOR && !model.requests);
    report("public_unsupported_variant", 32, rc);
    CHECK(bmi2_do_crt(NULL) == BMI2_E_NULL_PTR);

    if (EXPECT_FIXED) {
        initialize(32, true, BMI2_SPI_INTF);
        model.dev.config_size = 8190;
        rc = bmi2_do_crt(&model.dev);
        CHECK(rc == BMI2_E_INVALID_INPUT && !model.requests);
        report("public_declared_extent_rejected", 32, rc);
        initialize(32, true, BMI2_SPI_INTF);
        model.dev.config_file_ptr = NULL;
        rc = bmi2_do_crt(&model.dev);
        CHECK(rc == BMI2_E_NULL_PTR && !model.requests);
        report("public_null_config_rejected", 32, rc);
    }
    printf("{\"summary\":\"PASS_BOUNDED_SOFTWARE_ONLY\",\"cases\":%u,\"fixed\":%s,"
           "\"private_helper_called\":false,\"physical_or_SDK_IO\":false}\n",
           cases, EXPECT_FIXED ? "true" : "false");
    return 0;
}
