#define main frozen_bounds_main
#include "crt_public_path.c"
#undef main

static int early_error_case(unsigned requested, bool gyro)
{
    initialize(32, false, BMI2_SPI_INTF);
    model.dev.read_write_len = (uint16_t)requested;
    model.fault = FIRST_FEATURE_READ;
    model.callbacks = 0;
    model.trace_state = true;
    const unsigned before = model.dev.read_write_len;
    const int8_t rc = gyro ? bmi2_do_gyro_st(&model.dev) : bmi2_do_crt(&model.dev);
    const unsigned normalized = effective(requested);
    bool passed = before == requested && model.dev.read_write_len == normalized &&
                  rc == BMI2_E_COM_FAIL && model.fault_at == 2 && !model.after_fault &&
                  model.callbacks == 2 && model.delays == 2 && model.events == 4 &&
                  !model.requests && !model.accepted_bytes && !model.unsafe_requests &&
                  !model.triggers && !model.budget_hits;
    if (model.events == 4) {
        const event_t *events = model.trace;
        passed = passed &&
            events[0].operation == 'W' && events[0].address == BMI2_FEAT_PAGE_ADDR &&
            events[0].length == 1 && events[0].result == BMI2_INTF_RET_SUCCESS &&
            events[1].operation == 'D' && events[1].delay == BMI2_NORMAL_MODE_DELAY_IN_US &&
            events[2].operation == 'R' && events[2].address == BMI2_FEATURES_REG_ADDR &&
            events[2].length == (normalized < BMI2_FEAT_SIZE_IN_BYTES ?
                                normalized : BMI2_FEAT_SIZE_IN_BYTES) + 1 &&
            events[2].result == BMI2_E_COM_FAIL &&
            events[3].operation == 'D' && events[3].delay == BMI2_NORMAL_MODE_DELAY_IN_US;
        for (unsigned i = 0; i < 4; ++i) {
            passed = passed && events[i].caller_length == normalized;
        }
    }
    printf("{\"case\":\"early_feature_error\",\"public_entry\":\"%s\","
           "\"requested\":%u,\"pre_length\":%u,\"post_length\":%u,"
           "\"api_rc\":%d,\"io_callbacks\":%u,\"delay_callbacks\":%u,"
           "\"fault_callback\":%u,\"callbacks_after_fault\":%u,\"trigger_commands\":%u,"
           "\"upload_requests\":%u,\"unsafe_bytes_read\":0,\"budget_hits\":%u,"
           "\"error_preserved\":%s,\"trace\":[",
           gyro ? "bmi2_do_gyro_st" : "bmi2_do_crt", requested, before, model.dev.read_write_len,
           rc, model.callbacks, model.delays, model.fault_at, model.after_fault,
           model.triggers, model.requests, model.budget_hits, passed ? "true" : "false");
    for (unsigned i = 0; i < model.events; ++i) {
        const event_t event = model.trace[i];
        printf("%s[\"%c\",%u,%u,%u,%u,%d]", i ? "," : "", event.operation,
               event.address, event.length, event.delay, event.caller_length, event.result);
    }
    puts("]}");
    fflush(stdout);
    ++cases;
    return passed ? 0 : 3;
}

int main(int argc, char **argv)
{
    CHECK(argc == 2);
    if (strcmp(argv[1], "--bounds") == 0) {
        return frozen_bounds_main(1, argv);
    }
    const bool errors = strcmp(argv[1], "--early-errors") == 0;
    CHECK(errors || strcmp(argv[1], "--controls") == 0);
    const unsigned lengths[] = {0, 1, 19, 512, 65535, 32};
    const unsigned path_count = errors ? 1 : 3;
    for (unsigned path = 0; path < path_count; ++path) {
        for (unsigned gyro = 0; gyro < 2; ++gyro) {
            for (unsigned i = 0; i < sizeof(lengths) / sizeof(lengths[0]); ++i) {
                const int result = errors ? early_error_case(lengths[i], gyro != 0) :
                    state_case((enum state_path)path, lengths[i], gyro != 0);
                if (result) {
                    printf("{\"summary\":\"FAILED_NEW_CANDIDATE\",\"cases\":%u}\n", cases);
                    return result;
                }
            }
        }
    }
    printf("{\"summary\":\"COMPLETE_NEW_SOURCE_AUTHOR_HOST_ONLY\",\"cases\":%u,"
           "\"private_driver_helper_called\":false,\"physical_or_SDK_IO\":false}\n", cases);
    return 0;
}
