/* Generated DATA ONLY; no SDK configuration or hardware permission.
 * Accepted snapshot: ad2d59ba9f1cfd59e8ad553e9379798a76dfb650
 * Acceptance SHA256: 5615fb179957fe12b4b20d15911efa1e49a992261f5b23b1c79e3af30ad1c4c5
 * Original Evidence IDs/conditions: preparation_tables.json.
 * GPIO 0 is real BOOT_N. No unset bus/clock enum is emitted. */
#ifndef REV5_PREPARATION_PIN_DEFINITIONS_H
#define REV5_PREPARATION_PIN_DEFINITIONS_H
#include <stddef.h>
#define REV5_PREPARATION_HARDWARE_ACTIONS_AUTHORIZED 0
#define REV5_PREPARATION_SOURCE_REVISION "ad2d59ba9f1cfd59e8ad553e9379798a76dfb650"
#define REV5_PREPARATION_GPIO_COUNT 31u
#define REV5_PREPARATION_MODULE_PAD_COUNT 41u
/* Capacity only; NOT an SDK bus enum or selected controller. */
#define REV5_PREPARATION_HW_I2C_CAPACITY 2u

/* S39#/mcu_pad_gpio_net/4; S36#U201.4; S13#DS-MCU-102 */
#define REV5_PIN_IMU_CS_X_A_GPIO 4
#define REV5_PIN_IMU_CS_X_A_PAD "4"
#define REV5_PIN_IMU_CS_X_A_NET "IMU_CS_X_A"
#define REV5_PIN_IMU_CS_X_A_REF "U201"
/* S39#/mcu_pad_gpio_net/5; S36#U201.5; S13#DS-MCU-102 */
#define REV5_PIN_IMU_CS_X_B_GPIO 5
#define REV5_PIN_IMU_CS_X_B_PAD "5"
#define REV5_PIN_IMU_CS_X_B_NET "IMU_CS_X_B"
#define REV5_PIN_IMU_CS_X_B_REF "U201"
/* S39#/mcu_pad_gpio_net/6; S36#U201.6; S13#DS-MCU-102 */
#define REV5_PIN_IMU_CS_Y_A_GPIO 6
#define REV5_PIN_IMU_CS_Y_A_PAD "6"
#define REV5_PIN_IMU_CS_Y_A_NET "IMU_CS_Y_A"
#define REV5_PIN_IMU_CS_Y_A_REF "U201"
/* S39#/mcu_pad_gpio_net/7; S36#U201.7; S13#DS-MCU-102 */
#define REV5_PIN_IMU_CS_Y_B_GPIO 7
#define REV5_PIN_IMU_CS_Y_B_PAD "7"
#define REV5_PIN_IMU_CS_Y_B_NET "IMU_CS_Y_B"
#define REV5_PIN_IMU_CS_Y_B_REF "U201"
/* S39#/mcu_pad_gpio_net/8; S36#U201.8; S13#DS-MCU-102 */
#define REV5_PIN_IMU_CS_Z_A_GPIO 15
#define REV5_PIN_IMU_CS_Z_A_PAD "8"
#define REV5_PIN_IMU_CS_Z_A_NET "IMU_CS_Z_A"
#define REV5_PIN_IMU_CS_Z_A_REF "U201"
/* S39#/mcu_pad_gpio_net/9; S36#U201.9; S13#DS-MCU-102 */
#define REV5_PIN_IMU_CS_Z_B_GPIO 16
#define REV5_PIN_IMU_CS_Z_B_PAD "9"
#define REV5_PIN_IMU_CS_Z_B_NET "IMU_CS_Z_B"
#define REV5_PIN_IMU_CS_Z_B_REF "U201"
/* S39#/mcu_pad_gpio_net/19; S36#U201.19; S13#DS-IMU-094 */
#define REV5_PIN_IMU_MOSI_GPIO 11
#define REV5_PIN_IMU_MOSI_PAD "19"
#define REV5_PIN_IMU_MOSI_NET "IMU_MOSI"
#define REV5_PIN_IMU_MOSI_REF "U201"
/* S39#/mcu_pad_gpio_net/20; S36#U201.20; S13#DS-IMU-094 */
#define REV5_PIN_IMU_SCK_GPIO 12
#define REV5_PIN_IMU_SCK_PAD "20"
#define REV5_PIN_IMU_SCK_NET "IMU_SCK"
#define REV5_PIN_IMU_SCK_REF "U201"
/* S39#/mcu_pad_gpio_net/21; S36#U201.21; S13#DS-IMU-094 */
#define REV5_PIN_IMU_MISO_GPIO 13
#define REV5_PIN_IMU_MISO_PAD "21"
#define REV5_PIN_IMU_MISO_NET "IMU_MISO"
#define REV5_PIN_IMU_MISO_REF "U201"
/* S39#/mcu_pad_gpio_net/10; S36#U201.10; S13#DS-MCU-102 */
#define REV5_PIN_DRV_X_SPEED_GPIO 17
#define REV5_PIN_DRV_X_SPEED_PAD "10"
#define REV5_PIN_DRV_X_SPEED_NET "DRV_X_SPEED"
#define REV5_PIN_DRV_X_SPEED_REF "U201"
/* S39#/mcu_pad_gpio_net/11; S36#U201.11; S13#DS-MCU-102 */
#define REV5_PIN_DRV_Y_SPEED_GPIO 18
#define REV5_PIN_DRV_Y_SPEED_PAD "11"
#define REV5_PIN_DRV_Y_SPEED_NET "DRV_Y_SPEED"
#define REV5_PIN_DRV_Y_SPEED_REF "U201"
/* S39#/mcu_pad_gpio_net/22; S36#U201.22; S13#DS-MCU-102 */
#define REV5_PIN_DRV_Z_SPEED_GPIO 14
#define REV5_PIN_DRV_Z_SPEED_PAD "22"
#define REV5_PIN_DRV_Z_SPEED_NET "DRV_Z_SPEED"
#define REV5_PIN_DRV_Z_SPEED_REF "U201"
/* S39#/mcu_pad_gpio_net/23; S36#U201.23; S13#DS-MTR-094 */
#define REV5_PIN_DRV_X_DIR_GPIO 21
#define REV5_PIN_DRV_X_DIR_PAD "23"
#define REV5_PIN_DRV_X_DIR_NET "DRV_X_DIR"
#define REV5_PIN_DRV_X_DIR_REF "U201"
/* S39#/mcu_pad_gpio_net/38; S36#U201.38; S13#DS-MTR-094 */
#define REV5_PIN_DRV_Y_DIR_GPIO 2
#define REV5_PIN_DRV_Y_DIR_PAD "38"
#define REV5_PIN_DRV_Y_DIR_NET "DRV_Y_DIR"
#define REV5_PIN_DRV_Y_DIR_REF "U201"
/* S39#/mcu_pad_gpio_net/18; S36#U201.18; S13#DS-MTR-094 */
#define REV5_PIN_DRV_Z_DIR_GPIO 10
#define REV5_PIN_DRV_Z_DIR_PAD "18"
#define REV5_PIN_DRV_Z_DIR_NET "DRV_Z_DIR"
#define REV5_PIN_DRV_Z_DIR_REF "U201"
/* S39#/mcu_pad_gpio_net/28; S36#U201.28; S13#DS-MCU-102 */
#define REV5_PIN_DRV_X_FG_GPIO 35
#define REV5_PIN_DRV_X_FG_PAD "28"
#define REV5_PIN_DRV_X_FG_NET "DRV_X_FG"
#define REV5_PIN_DRV_X_FG_REF "U201"
/* S39#/mcu_pad_gpio_net/29; S36#U201.29; S13#DS-MCU-102 */
#define REV5_PIN_DRV_Y_FG_GPIO 36
#define REV5_PIN_DRV_Y_FG_PAD "29"
#define REV5_PIN_DRV_Y_FG_NET "DRV_Y_FG"
#define REV5_PIN_DRV_Y_FG_REF "U201"
/* S39#/mcu_pad_gpio_net/30; S36#U201.30; S13#DS-MCU-102 */
#define REV5_PIN_DRV_Z_FG_GPIO 37
#define REV5_PIN_DRV_Z_FG_PAD "30"
#define REV5_PIN_DRV_Z_FG_NET "DRV_Z_FG"
#define REV5_PIN_DRV_Z_FG_REF "U201"
/* S39#/mcu_pad_gpio_net/12; S36#U201.12; S13#DS-MCU-123 */
#define REV5_PIN_DRV_X_SCL_GPIO 8
#define REV5_PIN_DRV_X_SCL_PAD "12"
#define REV5_PIN_DRV_X_SCL_NET "DRV_X_SCL"
#define REV5_PIN_DRV_X_SCL_REF "U201"
/* S39#/mcu_pad_gpio_net/17; S36#U201.17; S13#DS-MCU-123 */
#define REV5_PIN_DRV_X_SDA_GPIO 9
#define REV5_PIN_DRV_X_SDA_PAD "17"
#define REV5_PIN_DRV_X_SDA_NET "DRV_X_SDA"
#define REV5_PIN_DRV_X_SDA_REF "U201"
/* S39#/mcu_pad_gpio_net/31; S36#U201.31; S13#DS-MCU-123 */
#define REV5_PIN_DRV_Y_SCL_GPIO 38
#define REV5_PIN_DRV_Y_SCL_PAD "31"
#define REV5_PIN_DRV_Y_SCL_NET "DRV_Y_SCL"
#define REV5_PIN_DRV_Y_SCL_REF "U201"
/* S39#/mcu_pad_gpio_net/32; S36#U201.32; S13#DS-MCU-123 */
#define REV5_PIN_DRV_Y_SDA_GPIO 39
#define REV5_PIN_DRV_Y_SDA_PAD "32"
#define REV5_PIN_DRV_Y_SDA_NET "DRV_Y_SDA"
#define REV5_PIN_DRV_Y_SDA_REF "U201"
/* S39#/mcu_pad_gpio_net/33; S36#U201.33; S13#DS-MCU-123 */
#define REV5_PIN_DRV_Z_SCL_GPIO 40
#define REV5_PIN_DRV_Z_SCL_PAD "33"
#define REV5_PIN_DRV_Z_SCL_NET "DRV_Z_SCL"
#define REV5_PIN_DRV_Z_SCL_REF "U201"
/* S39#/mcu_pad_gpio_net/34; S36#U201.34; S13#DS-MCU-123 */
#define REV5_PIN_DRV_Z_SDA_GPIO 41
#define REV5_PIN_DRV_Z_SDA_PAD "34"
#define REV5_PIN_DRV_Z_SDA_NET "DRV_Z_SDA"
#define REV5_PIN_DRV_Z_SDA_REF "U201"
/* S39#/mcu_pad_gpio_net/35; S36#U201.35; S40#section2 */
#define REV5_PIN_DRIVE_ENABLE_REQUEST_GPIO 42
#define REV5_PIN_DRIVE_ENABLE_REQUEST_PAD "35"
#define REV5_PIN_DRIVE_ENABLE_REQUEST_NET "DRIVE_ENABLE_REQUEST"
#define REV5_PIN_DRIVE_ENABLE_REQUEST_REF "U201"
/* S39#/mcu_pad_gpio_net/24; S36#U201.24; S40#section2 */
#define REV5_PIN_DRIVE_FAULT_INPUT_GPIO 47
#define REV5_PIN_DRIVE_FAULT_INPUT_PAD "24"
#define REV5_PIN_DRIVE_FAULT_INPUT_NET "DRIVE_FAULT_INPUT"
#define REV5_PIN_DRIVE_FAULT_INPUT_REF "U201"
/* S39#/mcu_pad_gpio_net/13; S36#U201.13; S29#Exact scope and epochs; S13#DS-MCU-140 */
#define REV5_PIN_USB_U_DM_MCU_GPIO 19
#define REV5_PIN_USB_U_DM_MCU_PAD "13"
#define REV5_PIN_USB_U_DM_MCU_NET "USB_U_DM_MCU"
#define REV5_PIN_USB_U_DM_MCU_REF "U201"
/* S39#/mcu_pad_gpio_net/14; S36#U201.14; S29#Exact scope and epochs; S13#DS-MCU-140; S13#DS-MCU-145 */
#define REV5_PIN_USB_U_DP_MCU_GPIO 20
#define REV5_PIN_USB_U_DP_MCU_PAD "14"
#define REV5_PIN_USB_U_DP_MCU_NET "USB_U_DP_MCU"
#define REV5_PIN_USB_U_DP_MCU_REF "U201"
/* S39#/mcu_pad_gpio_net/36; S36#U201.36; S13#DS-MCU-102; S13#DS-MCU-140 */
#define REV5_PIN_UART0_RX_GPIO 44
#define REV5_PIN_UART0_RX_PAD "36"
#define REV5_PIN_UART0_RX_NET "UART0_RX"
#define REV5_PIN_UART0_RX_REF "U201"
/* S39#/mcu_pad_gpio_net/37; S36#U201.37; S13#DS-MCU-129; S13#DS-MCU-140 */
#define REV5_PIN_UART0_TX_GPIO 43
#define REV5_PIN_UART0_TX_PAD "37"
#define REV5_PIN_UART0_TX_NET "UART0_TX"
#define REV5_PIN_UART0_TX_REF "U201"
/* S39#/mcu_pad_gpio_net/27; S36#U201.27; S13#DS-MCU-120 */
#define REV5_PIN_BOOT_N_GPIO 0
#define REV5_PIN_BOOT_N_PAD "27"
#define REV5_PIN_BOOT_N_NET "BOOT_N"
#define REV5_PIN_BOOT_N_REF "U201"

/* gpio_decimal is a label, NULL for non-GPIO; NC is not assigned IO. */
typedef struct {
    const char *id, *net, *ref, *pad, *gpio_decimal, *kind;
} rev5_preparation_module_pin;
static const rev5_preparation_module_pin rev5_preparation_module_pins[] = {
    {"IMU_CS_X_A", "IMU_CS_X_A", "U201", "4", "4", "CONNECTED_GPIO"},
    {"IMU_CS_X_B", "IMU_CS_X_B", "U201", "5", "5", "CONNECTED_GPIO"},
    {"IMU_CS_Y_A", "IMU_CS_Y_A", "U201", "6", "6", "CONNECTED_GPIO"},
    {"IMU_CS_Y_B", "IMU_CS_Y_B", "U201", "7", "7", "CONNECTED_GPIO"},
    {"IMU_CS_Z_A", "IMU_CS_Z_A", "U201", "8", "15", "CONNECTED_GPIO"},
    {"IMU_CS_Z_B", "IMU_CS_Z_B", "U201", "9", "16", "CONNECTED_GPIO"},
    {"IMU_MOSI", "IMU_MOSI", "U201", "19", "11", "CONNECTED_GPIO"},
    {"IMU_SCK", "IMU_SCK", "U201", "20", "12", "CONNECTED_GPIO"},
    {"IMU_MISO", "IMU_MISO", "U201", "21", "13", "CONNECTED_GPIO"},
    {"DRV_X_SPEED", "DRV_X_SPEED", "U201", "10", "17", "CONNECTED_GPIO"},
    {"DRV_Y_SPEED", "DRV_Y_SPEED", "U201", "11", "18", "CONNECTED_GPIO"},
    {"DRV_Z_SPEED", "DRV_Z_SPEED", "U201", "22", "14", "CONNECTED_GPIO"},
    {"DRV_X_DIR", "DRV_X_DIR", "U201", "23", "21", "CONNECTED_GPIO"},
    {"DRV_Y_DIR", "DRV_Y_DIR", "U201", "38", "2", "CONNECTED_GPIO"},
    {"DRV_Z_DIR", "DRV_Z_DIR", "U201", "18", "10", "CONNECTED_GPIO"},
    {"DRV_X_FG", "DRV_X_FG", "U201", "28", "35", "CONNECTED_GPIO"},
    {"DRV_Y_FG", "DRV_Y_FG", "U201", "29", "36", "CONNECTED_GPIO"},
    {"DRV_Z_FG", "DRV_Z_FG", "U201", "30", "37", "CONNECTED_GPIO"},
    {"DRV_X_SCL", "DRV_X_SCL", "U201", "12", "8", "CONNECTED_GPIO"},
    {"DRV_X_SDA", "DRV_X_SDA", "U201", "17", "9", "CONNECTED_GPIO"},
    {"DRV_Y_SCL", "DRV_Y_SCL", "U201", "31", "38", "CONNECTED_GPIO"},
    {"DRV_Y_SDA", "DRV_Y_SDA", "U201", "32", "39", "CONNECTED_GPIO"},
    {"DRV_Z_SCL", "DRV_Z_SCL", "U201", "33", "40", "CONNECTED_GPIO"},
    {"DRV_Z_SDA", "DRV_Z_SDA", "U201", "34", "41", "CONNECTED_GPIO"},
    {"DRIVE_ENABLE_REQUEST", "DRIVE_ENABLE_REQUEST", "U201", "35", "42", "CONNECTED_GPIO"},
    {"DRIVE_FAULT_INPUT", "DRIVE_FAULT_INPUT", "U201", "24", "47", "CONNECTED_GPIO"},
    {"USB_U_DM_MCU", "USB_U_DM_MCU", "U201", "13", "19", "CONNECTED_GPIO"},
    {"USB_U_DP_MCU", "USB_U_DP_MCU", "U201", "14", "20", "CONNECTED_GPIO"},
    {"UART0_RX", "UART0_RX", "U201", "36", "44", "CONNECTED_GPIO"},
    {"UART0_TX", "UART0_TX", "U201", "37", "43", "CONNECTED_GPIO"},
    {"BOOT_N", "BOOT_N", "U201", "27", "0", "CONNECTED_GPIO"},
    {"NC-U201-15", NULL, "U201", "15", "3", "NC"},
    {"NC-U201-16", NULL, "U201", "16", "46", "NC"},
    {"NC-U201-26", NULL, "U201", "26", "45", "NC"},
    {"NC-U201-39", NULL, "U201", "39", "1", "NC"},
    {"NC-U201-25", NULL, "U201", "25", "48", "NC"},
    {"U201-POWER", "LOGIC_3V3", "U201", "2", NULL, "NON_GPIO"},
    {"U201-GND1", "GND", "U201", "1", NULL, "NON_GPIO"},
    {"U201-GND40", "GND", "U201", "40", NULL, "NON_GPIO"},
    {"U201-EPAD", "GND", "U201", "41", NULL, "NON_GPIO"},
    {"MCU_EN", "MCU_EN", "U201", "3", NULL, "NON_GPIO"},
};

typedef struct {
    const char *id, *sensor_ref, *cs_net, *host_ref, *host_pad;
    unsigned host_gpio;
    const char *sensor_cs_pad, *sensor_miso_pad, *sensor_sck_pad, *sensor_mosi_pad;
} rev5_preparation_imu_identity;
static const rev5_preparation_imu_identity rev5_preparation_imus[] = {
    {"X_A", "U101", "IMU_CS_X_A", "U201", "4", 4, "12", "1", "13", "14"},
    {"X_B", "U102", "IMU_CS_X_B", "U201", "5", 5, "12", "1", "13", "14"},
    {"Y_A", "U103", "IMU_CS_Y_A", "U201", "6", 6, "12", "1", "13", "14"},
    {"Y_B", "U104", "IMU_CS_Y_B", "U201", "7", 7, "12", "1", "13", "14"},
    {"Z_A", "U105", "IMU_CS_Z_A", "U201", "8", 15, "12", "1", "13", "14"},
    {"Z_B", "U106", "IMU_CS_Z_B", "U201", "9", 16, "12", "1", "13", "14"},
};

/* Source endpoint PAIRS ONLY: the fifteen bridges remain UNBRIDGED. */
typedef struct {
    const char *id, *axis, *function, *host_ref, *host_pad, *host_net;
    unsigned host_gpio;
    const char *driver_ref, *driver_pad, *driver_net;
    const char *native_host_direction, *native_driver_direction, *transport_direction;
    const char *host_rail, *driver_rail, *vm_rail, *return_net;
} rev5_preparation_driver_pair;
static const rev5_preparation_driver_pair rev5_preparation_driver_pairs[] = {
    {"DRV_X_SPEED", "X", "SPEED", "U201", "10", "DRV_X_SPEED", 17, "U301", "13", "DRV_X_SPEED_D", "bidirectional", "input", "MCU_TO_DRIVER", "LOGIC_3V3", "DRV_3V3_X", "VM_X", "GND"},
    {"DRV_X_DIR", "X", "DIR", "U201", "23", "DRV_X_DIR", 21, "U301", "14", "DRV_X_DIR_D", "bidirectional", "input", "MCU_TO_DRIVER", "LOGIC_3V3", "DRV_3V3_X", "VM_X", "GND"},
    {"DRV_X_FG", "X", "FG", "U201", "28", "DRV_X_FG", 35, "U301", "12", "DRV_X_FG_D", "bidirectional", "open_collector", "DRIVER_TO_MCU", "LOGIC_3V3", "DRV_3V3_X", "VM_X", "GND"},
    {"DRV_X_SCL", "X", "SCL", "U201", "12", "DRV_X_SCL", 8, "U301", "10", "DRV_X_SCL_D", "bidirectional", "input", "BIDIRECTIONAL_OPEN_DRAIN", "LOGIC_3V3", "DRV_3V3_X", "VM_X", "GND"},
    {"DRV_X_SDA", "X", "SDA", "U201", "17", "DRV_X_SDA", 9, "U301", "11", "DRV_X_SDA_D", "bidirectional", "bidirectional", "BIDIRECTIONAL_OPEN_DRAIN", "LOGIC_3V3", "DRV_3V3_X", "VM_X", "GND"},
    {"DRV_Y_SPEED", "Y", "SPEED", "U201", "11", "DRV_Y_SPEED", 18, "U302", "13", "DRV_Y_SPEED_D", "bidirectional", "input", "MCU_TO_DRIVER", "LOGIC_3V3", "DRV_3V3_Y", "VM_Y", "GND"},
    {"DRV_Y_DIR", "Y", "DIR", "U201", "38", "DRV_Y_DIR", 2, "U302", "14", "DRV_Y_DIR_D", "bidirectional", "input", "MCU_TO_DRIVER", "LOGIC_3V3", "DRV_3V3_Y", "VM_Y", "GND"},
    {"DRV_Y_FG", "Y", "FG", "U201", "29", "DRV_Y_FG", 36, "U302", "12", "DRV_Y_FG_D", "bidirectional", "open_collector", "DRIVER_TO_MCU", "LOGIC_3V3", "DRV_3V3_Y", "VM_Y", "GND"},
    {"DRV_Y_SCL", "Y", "SCL", "U201", "31", "DRV_Y_SCL", 38, "U302", "10", "DRV_Y_SCL_D", "bidirectional", "input", "BIDIRECTIONAL_OPEN_DRAIN", "LOGIC_3V3", "DRV_3V3_Y", "VM_Y", "GND"},
    {"DRV_Y_SDA", "Y", "SDA", "U201", "32", "DRV_Y_SDA", 39, "U302", "11", "DRV_Y_SDA_D", "bidirectional", "bidirectional", "BIDIRECTIONAL_OPEN_DRAIN", "LOGIC_3V3", "DRV_3V3_Y", "VM_Y", "GND"},
    {"DRV_Z_SPEED", "Z", "SPEED", "U201", "22", "DRV_Z_SPEED", 14, "U303", "13", "DRV_Z_SPEED_D", "bidirectional", "input", "MCU_TO_DRIVER", "LOGIC_3V3", "DRV_3V3_Z", "VM_Z", "GND"},
    {"DRV_Z_DIR", "Z", "DIR", "U201", "18", "DRV_Z_DIR", 10, "U303", "14", "DRV_Z_DIR_D", "bidirectional", "input", "MCU_TO_DRIVER", "LOGIC_3V3", "DRV_3V3_Z", "VM_Z", "GND"},
    {"DRV_Z_FG", "Z", "FG", "U201", "30", "DRV_Z_FG", 37, "U303", "12", "DRV_Z_FG_D", "bidirectional", "open_collector", "DRIVER_TO_MCU", "LOGIC_3V3", "DRV_3V3_Z", "VM_Z", "GND"},
    {"DRV_Z_SCL", "Z", "SCL", "U201", "33", "DRV_Z_SCL", 40, "U303", "10", "DRV_Z_SCL_D", "bidirectional", "input", "BIDIRECTIONAL_OPEN_DRAIN", "LOGIC_3V3", "DRV_3V3_Z", "VM_Z", "GND"},
    {"DRV_Z_SDA", "Z", "SDA", "U201", "34", "DRV_Z_SDA", 41, "U303", "11", "DRV_Z_SDA_D", "bidirectional", "bidirectional", "BIDIRECTIONAL_OPEN_DRAIN", "LOGIC_3V3", "DRV_3V3_Z", "VM_Z", "GND"},
};

/* Domain identities are NOT controller instances or axis assignments.
 * Named VM supplies remain UNPROVIDED; no power connection is made. */
typedef struct {
    const char *id, *axis, *driver_ref;
    unsigned address_7bit;
    const char *vm_net, *local_3v3_net;
} rev5_preparation_driver_domain;
static const rev5_preparation_driver_domain rev5_preparation_driver_domains[] = {
    {"DRV_I2C_X", "X", "U301", 82, "VM_X", "DRV_3V3_X"},
    {"DRV_I2C_Y", "Y", "U302", 82, "VM_Y", "DRV_3V3_Y"},
    {"DRV_I2C_Z", "Z", "U303", 82, "VM_Z", "DRV_3V3_Z"},
};

#endif
