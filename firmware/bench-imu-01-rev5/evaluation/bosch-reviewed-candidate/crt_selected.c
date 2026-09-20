/* Reuse the immutable public-path model, not a private Bosch helper.
 * Its immediate-ready behavior intentionally does NOT qualify C3. */
#define main frozen_bounds_main
#include "crt_public_path.c"
#undef main

typedef struct {
    unsigned kind, gyro, spi, aps, initial, requested, fifo, arg, fault, at;
} input_t;
typedef struct {
    input_t input;
    unsigned expected_length, initial_reads, tail_reads, upload_addresses, delays, active_chunk;
    unsigned normalized_at_first_callback;
    bool initial_done, active, command_for_chunk, tail_phase, tail_done;
    uint64_t digest;
} selected_t;
static selected_t selected;
static char current_id[128];

static void observe(char operation, uint8_t address, uint32_t length)
{
    CHECK(model.dev.read_write_len == selected.expected_length);
    if (!model.callbacks) {
        selected.normalized_at_first_callback = model.dev.read_write_len;
    }
    selected.digest = (selected.digest ^ (unsigned char)operation) * UINT64_C(1099511628211);
    selected.digest = (selected.digest ^ address) * UINT64_C(1099511628211);
    selected.digest = (selected.digest ^ length) * UINT64_C(1099511628211);
}

static BMI2_INTF_RETURN_TYPE selected_failure(void)
{
    CHECK(callback_budget(&model));
    return inject(&model);
}

static bool feature_address(uint8_t reg)
{
    return reg >= BMI2_FEATURES_REG_ADDR && reg < BMI2_FEATURES_REG_ADDR + BMI2_FEAT_SIZE_IN_BYTES;
}

static BMI2_INTF_RETURN_TYPE selected_read(uint8_t address, uint8_t *data,
                                          uint32_t length, void *context)
{
    CHECK(context == &model);
    observe('R', address, length);
    const uint8_t reg = address & BMI2_SPI_WR_MASK;
    CHECK(address == (uint8_t)(reg | (selected.input.spi ? BMI2_SPI_RD_MASK : 0)));
    const bool feature = feature_address(reg);
    if (feature && !selected.initial_done) {
        const unsigned part = selected.initial_reads++;
        const unsigned chunk = selected.expected_length < 16 ? selected.expected_length : 16;
        const unsigned remaining = 16 - part * chunk;
        CHECK(reg == BMI2_FEATURES_REG_ADDR + part * chunk);
        CHECK(length == (remaining < chunk ? remaining : chunk) + selected.input.spi);
        if (selected.input.kind == 7 && selected.input.fault == 2 && part == selected.input.at) {
            return selected_failure();
        }
        selected.initial_done = selected.initial_reads == (16 + chunk - 1) / chunk;
    } else if (feature && selected.tail_phase) {
        const unsigned part = selected.tail_reads++;
        if (selected.input.kind == 9 && selected.input.fault == 2 && part == selected.input.at) {
            return selected_failure();
        }
    }
    if (selected.input.kind == 8 && selected.active && selected.active_chunk == selected.input.at &&
        reg == BMI2_GYR_CRT_CONF_ADDR &&
        selected.input.fault == (selected.command_for_chunk ? 7u : 5u)) {
        return selected_failure();
    }
    return read_registers_impl(address, data, length, context);
}

static BMI2_INTF_RETURN_TYPE selected_write(uint8_t address, const uint8_t *data,
                                           uint32_t length, void *context)
{
    CHECK(context == &model);
    observe('W', address, length);
    const uint8_t reg = address & BMI2_SPI_WR_MASK;
    CHECK(reg == address);
    const unsigned full_bytes = CRT_BYTES - CRT_BYTES % selected.expected_length;
    if (reg == BMI2_FEAT_PAGE_ADDR && !selected.initial_done &&
        selected.input.kind == 7 && selected.input.fault == 1) {
        return selected_failure();
    }
    if (reg == BMI2_FEAT_PAGE_ADDR && model.accepted_bytes == full_bytes &&
        full_bytes < CRT_BYTES && !selected.tail_done) {
        selected.tail_phase = true;
        if (selected.input.kind == 9 && selected.input.fault == 1) {
            return selected_failure();
        }
    }
    if (selected.tail_phase && feature_address(reg)) {
        CHECK(reg == BMI2_FEATURES_REG_ADDR + BMI270_MAX_BURST_LEN_STRT_ADDR);
        CHECK(length == 2 && data[0] == 1);
        if (selected.input.kind == 9 && selected.input.fault == 8) {
            return selected_failure();
        }
        selected.tail_phase = false;
        selected.tail_done = true;
    }
    if (reg == BMI2_INIT_ADDR_0) {
        ++selected.upload_addresses;
        selected.active = true;
        selected.active_chunk = model.accepted_requests;
        selected.command_for_chunk = false;
        if (selected.input.kind == 8 && selected.input.fault == 3 &&
            selected.active_chunk == selected.input.at) {
            return selected_failure();
        }
    }
    if (reg == BMI2_INIT_DATA_ADDR && selected.input.kind == 8 &&
        selected.input.fault == 4 && selected.active_chunk == selected.input.at) {
        const uintptr_t begin = (uintptr_t)model.dev.config_file_ptr;
        const uintptr_t ptr = (uintptr_t)data;
        CHECK(begin && ptr >= begin && ptr - begin <= CRT_END);
        const unsigned offset = (unsigned)(ptr - begin);
        CHECK(offset >= CRT_START && length <= CRT_END - offset);
        CHECK(offset == model.init_offset && !(offset & 1u) && !(length & 1u));
        CHECK(model.requests < MAX_REQUESTS);
        model.spans[model.requests++] = (request_t){offset, length, model.init_offset, false};
        return selected_failure();
    }
    if (reg == BMI2_CMD_REG_ADDR && length == 1 && data[0] == BMI2_G_TRIGGER_CMD && selected.active) {
        if (selected.input.kind == 8 && selected.input.fault == 6 &&
            selected.active_chunk == selected.input.at) {
            return selected_failure();
        }
        selected.command_for_chunk = true;
    }
    return write_registers_impl(address, data, length, context);
}

static void selected_delay(uint32_t period, void *context)
{
    CHECK(context == &model && period <= 200000);
    ++selected.delays;
}

static void check_prefix(void)
{
    unsigned cursor = CRT_START;
    const unsigned chunk = selected.expected_length;
    const unsigned full_end = CRT_END - CRT_BYTES % chunk;
    for (unsigned i = 0; i < model.requests; ++i) {
        const request_t span = model.spans[i];
        CHECK(span.offset == cursor && span.encoded_offset == cursor);
        CHECK(span.length == (cursor < full_end ? chunk : 2));
        CHECK(span.length <= CRT_END - cursor && !(span.offset & 1u) && !(span.length & 1u));
        if (span.accepted) {
            cursor += span.length;
        } else {
            CHECK(i + 1 == model.requests && selected.input.fault == 4);
        }
    }
    CHECK(model.accepted_bytes == cursor - CRT_START && !model.unsafe_requests);
}

static void run_case(input_t input)
{
    initialize(input.initial, input.fifo != 0, input.spi ? BMI2_SPI_INTF : BMI2_I2C_INTF);
    memset(&selected, 0, sizeof(selected));
    selected.input = input;
    selected.digest = UINT64_C(14695981039346656037);
    if (input.kind != 1) {
        model.dev.read_write_len = (uint16_t)input.requested;
    }
    selected.expected_length = input.kind == 4 ? input.requested : effective(model.dev.read_write_len);
    if (input.aps) {
        CHECK(bmi2_set_adv_power_save(BMI2_ENABLE, &model.dev) == BMI2_OK);
    }
    if (input.kind == 3) {
        model.regs[BMI2_GYR_CRT_CONF_ADDR] |= BMI2_GYR_CRT_RUNNING_MASK;
    } else if (input.kind == 4) {
        model.dev.variant_feature = 0;
    } else if (input.kind == 5) {
        model.dev.config_size = (uint16_t)input.arg;
    }
    model.callbacks = 0;
    model.dev.read = selected_read;
    model.dev.write = selected_write;
    model.dev.delay_us = selected_delay;
    struct bmi2_dev *device = &model.dev;
    if (input.kind == 6) {
        switch (input.arg) {
            case 0: model.dev.config_file_ptr = NULL; break;
            case 1: device = NULL; break;
            case 2: model.dev.read = NULL; break;
            case 3: model.dev.write = NULL; break;
            case 4: model.dev.delay_us = NULL; break;
            default: CHECK(false);
        }
    }
    const unsigned before = model.dev.read_write_len;
    const int8_t result = input.gyro ? bmi2_do_gyro_st(device) : bmi2_do_crt(device);
    int8_t expected = BMI2_OK;
    if (input.kind == 3) {
        expected = BMI2_E_ST_ALREADY_RUNNING;
        const unsigned chunk = selected.expected_length;
        const unsigned feature_reads = chunk < 16 ? (16 + chunk - 1) / chunk : 1;
        CHECK(model.callbacks == feature_reads + 2 && !model.triggers);
    } else if (input.kind == 4) {
        expected = BMI2_E_INVALID_SENSOR;
        CHECK(!model.callbacks && model.dev.read_write_len == before);
    } else if (input.kind == 5 || input.kind == 6) {
        expected = input.kind == 5 ? BMI2_E_INVALID_INPUT : BMI2_E_NULL_PTR;
        CHECK(!model.requests && !selected.upload_addresses);
        if (input.kind == 6 && input.arg) {
            CHECK(!model.callbacks && model.dev.read_write_len == before);
        } else {
            CHECK(model.callbacks && model.triggers);
        }
    } else if (input.kind >= 7) {
        expected = BMI2_E_COM_FAIL;
        CHECK(model.fault_at && !model.after_fault);
        if (input.kind == 7) {
            const unsigned expected_io = 2 * input.aps + (input.fault == 1 ? 1 : 2 + input.at);
            CHECK(model.callbacks == expected_io && selected.delays == expected_io);
            CHECK(!model.requests && !model.triggers && !selected.upload_addresses);
            CHECK(model.dev.aps_status == BMI2_DISABLE &&
                  !(model.regs[BMI2_PWR_CONF_ADDR] & BMI2_ADV_POW_EN_MASK));
        } else if (input.kind == 8) {
            CHECK(model.accepted_requests == input.at + (input.fault >= 5));
            check_prefix();
        } else {
            CHECK(model.accepted_bytes == CRT_BYTES - CRT_BYTES % selected.expected_length);
            CHECK(model.accepted_requests == CRT_BYTES / selected.expected_length);
            check_prefix();
        }
    }
    CHECK(result == expected && !model.budget_hits && !model.unsafe_requests && !model.after_fault);
    if (input.kind == 0 || input.kind == 1) {
        complete_spans(selected.expected_length);
        CHECK(model.features[BMI2_PAGE_1][BMI270_MAX_BURST_LEN_STRT_ADDR] == 0);
    } else if (input.kind <= 4) {
        CHECK(!model.requests);
        CHECK(model.triggers == (input.kind == 2 ? 1u : 0u));
    }
    if (result == BMI2_OK) {
        CHECK(model.dev.aps_status == input.aps);
        CHECK((model.regs[BMI2_PWR_CONF_ADDR] & BMI2_ADV_POW_EN_MASK) ==
              (input.aps ? BMI2_ADV_POW_EN_MASK : 0));
    }
    if (model.callbacks) {
        CHECK(selected.normalized_at_first_callback == selected.expected_length);
        CHECK(model.dev.read_write_len == selected.expected_length);
    }
    printf("{\"id\":\"%s\",\"api_rc\":%d,\"before_length\":%u,\"after_length\":%u,"
           "\"io_callbacks\":%u,\"delay_callbacks\":%u,\"fault_callback\":%u,"
           "\"callbacks_after_fault\":%u,\"upload_requests\":%u,\"accepted_bytes\":%u,"
           "\"trigger_commands\":%u,\"initial_feature_reads\":%u,\"aps_cached\":%u,"
           "\"io_digest\":\"%016llx\",\"unsafe_requests\":0,\"passed\":true}\n",
           current_id, result, before, model.dev.read_write_len, model.callbacks, selected.delays,
           model.fault_at, model.after_fault, model.requests, model.accepted_bytes, model.triggers,
           selected.initial_reads, model.dev.aps_status, (unsigned long long)selected.digest);
    fflush(stdout);
}

int main(int argc, char **argv)
{
    CHECK(argc == 2);
    FILE *input = fopen(argv[1], "r");
    CHECK(input != NULL);
    input_t row;
    unsigned count = 0;
    int fields;
    while ((fields = fscanf(input, "%127s %u %u %u %u %u %u %u %u %u %u",
                            current_id, &row.kind, &row.gyro, &row.spi, &row.aps,
                            &row.initial, &row.requested, &row.fifo, &row.arg, &row.fault, &row.at)) != EOF) {
        CHECK(fields == 11);
        run_case(row);
        ++count;
    }
    CHECK(!ferror(input) && fclose(input) == 0);
    printf("{\"summary\":\"COMPLETE_SELECTED_AUTHOR_HOST_ONLY\",\"cases\":%u}\n", count);
    return 0;
}
