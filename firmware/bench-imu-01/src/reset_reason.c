#include "reset_reason.h"
#include "stm32g031_regs.h"
#include "usart2.h"

void reset_reason_report(void)
{
    uint32_t csr = RCC->CSR;
    int any = 0;

    usart2_write_str("RESET_REASON:");

    if (csr & RCC_CSR_PINRSTF)
    {
        usart2_write_str(" NRST_PIN(SW1_or_debugger)");
        any = 1;
    }
    if (csr & RCC_CSR_PWRRSTF)
    {
        usart2_write_str(" POWER_ON");
        any = 1;
    }
    if (csr & RCC_CSR_SFTRSTF)
    {
        usart2_write_str(" SOFTWARE");
        any = 1;
    }
    if (csr & RCC_CSR_IWDGRSTF)
    {
        usart2_write_str(" INDEPENDENT_WATCHDOG");
        any = 1;
    }
    if (csr & RCC_CSR_WWDGRSTF)
    {
        usart2_write_str(" WINDOW_WATCHDOG");
        any = 1;
    }
    if (csr & RCC_CSR_OBLRSTF)
    {
        usart2_write_str(" OPTION_BYTE_LOADER");
        any = 1;
    }
    if (csr & RCC_CSR_LPWRRSTF)
    {
        usart2_write_str(" ILLEGAL_LOW_POWER_ENTRY");
        any = 1;
    }
    if (!any)
    {
        usart2_write_str(" NONE_RECORDED");
    }
    usart2_write_str("\r\n");

    /* Clear all *RSTF flags so a future reset's report isn't polluted by
     * this one's cause. */
    RCC->CSR |= RCC_CSR_RMVF;
}
