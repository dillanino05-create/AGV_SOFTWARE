-- Found Git: C:/Program Files/Git/cmd/git.exe (found version "2.54.0.windows.1")
-- Component directory C:/esp/v6.0.1/esp-idf/components/mqtt does not contain a CMakeLists.txt file. No component will be added
-- Minimal build - OFF
-- The C compiler identification is GNU 15.2.0
-- The CXX compiler identification is GNU 15.2.0
-- The ASM compiler identification is GNU
-- Found assembler: C:/Espressif/tools/xtensa-esp-elf/esp-15.2.0_20251204/xtensa-esp-elf/bin/xtensa-esp32s3-elf-gcc.exe
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working C compiler: C:/Espressif/tools/xtensa-esp-elf/esp-15.2.0_20251204/xtensa-esp-elf/bin/xtensa-esp32s3-elf-gcc.exe - skipped
-- Detecting C compile features
-- Detecting C compile features - done
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Check for working CXX compiler: C:/Espressif/tools/xtensa-esp-elf/esp-15.2.0_20251204/xtensa-esp-elf/bin/xtensa-esp32s3-elf-g++.exe - skipped
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- git rev-parse returned 'fatal: not a git repository (or any of the parent directories): .git'
-- Could not use 'git describe' to determine PROJECT_VER.
-- Building ESP-IDF components for target esp32s3
-- ESP-TEE is currently supported only on the esp32c6;esp32h2;esp32c5;esp32c61 SoCs
-- KCONFIG_REPORT_VERBOSITY not set, using default
-- Project sdkconfig file D:/ESP_S3/sdkconfig
Configuration Report                                                           
+-----------------------------------------------------------------------------+
|  Parser Version: 1                                                          |
|  Verbosity: default                                                         |
|  Defaults policy: sdkconfig                                                 |
|  Status: Finished with notifications                                        |
|                                                                             |
| Disabled Symbols/Choices With User-Set Value                                |
| +-------------------------------------------------------------------------+ |
| | * ESP_WIFI_SOFTAP_SAE_SUPPORT (defined at                               | |
| | C:/esp/v6.0.1/esp-idf/components/esp_wifi/Kconfig:324) with user-set    | |
| | value n from C:\Users\usuario\AppData\Local\Temp\kconfgen_tmpvpw7lcop   | |
| +-------------------------------------------------------------------------+ |
+-----------------------------------------------------------------------------+
Loading defaults file D:/ESP_S3/sdkconfig.defaults...
-- Compiler supported targets: xtensa-esp-elf
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- App "wifi_verificacion" version: 1
-- Found Python3: C:/Espressif/tools/python/v6.0.1/venv/Scripts/python.exe (found version "3.14.3") found components: Interpreter
-- Performing Test CMAKE_HAVE_LIBC_PTHREAD
-- Performing Test CMAKE_HAVE_LIBC_PTHREAD - Success
-- Found Threads: TRUE
-- Performing Test C_COMPILER_SUPPORTS_WFORMAT_SIGNEDNESS
-- Performing Test C_COMPILER_SUPPORTS_WFORMAT_SIGNEDNESS - Success
-- Setting up mbedtls configuration
-- Linkage type is PUBLIC
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_hal_wdt/esp32s3/rom.wdt.ld
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_system/ld/esp32s3/memory.ld.in
--   -> Preprocessing .in script: C:/esp/v6.0.1/esp-idf/components/esp_system/ld/esp32s3/memory.ld.in
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_system/ld/esp32s3/sections.ld.in
--   -> Preprocessing .in script: C:/esp/v6.0.1/esp-idf/components/esp_system/ld/esp32s3/sections.ld.in
--   -> Applying ldgen processing: D:/ESP_S3/build/esp-idf/esp_system/ld/sections.ld.in
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_rom/esp32s3/ld/esp32s3.rom.ld
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_rom/esp32s3/ld/esp32s3.rom.api.ld
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_rom/esp32s3/ld/esp32s3.rom.bt_funcs.ld
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_rom/esp32s3/ld/esp32s3.rom.libgcc.ld
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_rom/esp32s3/ld/esp32s3.rom.version.ld
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_rom/esp32s3/ld/esp32s3.rom.ble_master.ld
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_rom/esp32s3/ld/esp32s3.rom.ble_50.ld
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_rom/esp32s3/ld/esp32s3.rom.ble_smp.ld
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_rom/esp32s3/ld/esp32s3.rom.ble_dtm.ld
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_rom/esp32s3/ld/esp32s3.rom.ble_test.ld
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_rom/esp32s3/ld/esp32s3.rom.ble_scan.ld
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_rom/esp32s3/ld/esp32s3.rom.libc.ld
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/soc/esp32s3/ld/esp32s3.peripherals.ld
-- Component idf::esp_trace will be linked with -Wl,--whole-archive
-- Components: app_trace app_update bootloader bootloader_support bt cmock console cxx driver efuse esp-tls esp_adc esp_app_format esp_blockdev esp_blockdev_util esp_bootloader_format esp_coex esp_common esp_driver_ana_cmpr esp_driver_bitscrambler esp_driver_cam esp_driver_dac esp_driver_dma esp_driver_gpio esp_driver_gptimer esp_driver_i2c esp_driver_i2s esp_driver_i3c esp_driver_isp esp_driver_jpeg esp_driver_ledc esp_driver_mcpwm esp_driver_parlio esp_driver_pcnt esp_driver_ppa esp_driver_rmt esp_driver_sd_intf esp_driver_sdio esp_driver_sdm esp_driver_sdmmc esp_driver_sdspi esp_driver_spi esp_driver_touch_sens esp_driver_tsens esp_driver_twai esp_driver_uart esp_driver_usb_serial_jtag esp_eth esp_event esp_gdbstub esp_hal_ana_cmpr esp_hal_ana_conv esp_hal_cam esp_hal_clock esp_hal_dma esp_hal_gpio esp_hal_gpspi esp_hal_i2c esp_hal_i2s esp_hal_ieee802154 esp_hal_jpeg esp_hal_lcd esp_hal_ledc esp_hal_mcpwm esp_hal_mspi esp_hal_parlio esp_hal_pcnt esp_hal_pmu esp_hal_ppa esp_hal_rmt esp_hal_rtc_timer esp_hal_sd esp_hal_security esp_hal_timg esp_hal_touch_sens esp_hal_twai esp_hal_uart esp_hal_usb esp_hal_wdt esp_hid esp_http_client esp_http_server esp_https_ota esp_https_server esp_hw_support esp_lcd esp_libc esp_local_ctrl esp_mm esp_netif esp_netif_stack esp_partition esp_phy esp_pm esp_psram esp_ringbuf esp_rom esp_security esp_stdio esp_system esp_timer esp_trace esp_usb_cdc_rom_console esp_wifi espcoredump esptool_py fatfs freertos hal heap http_parser idf_test ieee802154 log lwip main mbedtls nvs_flash nvs_sec_provider openthread partition_table perfmon protobuf-c protocomm pthread rt sdmmc soc spi_flash spiffs tcp_transport ulp unity vfs wear_levelling wpa_supplicant xtensa
-- Component paths: C:/esp/v6.0.1/esp-idf/components/app_trace C:/esp/v6.0.1/esp-idf/components/app_update C:/esp/v6.0.1/esp-idf/components/bootloader C:/esp/v6.0.1/esp-idf/components/bootloader_support C:/esp/v6.0.1/esp-idf/components/bt C:/esp/v6.0.1/esp-idf/components/cmock C:/esp/v6.0.1/esp-idf/components/console C:/esp/v6.0.1/esp-idf/components/cxx C:/esp/v6.0.1/esp-idf/components/driver C:/esp/v6.0.1/esp-idf/components/efuse C:/esp/v6.0.1/esp-idf/components/esp-tls C:/esp/v6.0.1/esp-idf/components/esp_adc C:/esp/v6.0.1/esp-idf/components/esp_app_format C:/esp/v6.0.1/esp-idf/components/esp_blockdev C:/esp/v6.0.1/esp-idf/components/esp_blockdev_util C:/esp/v6.0.1/esp-idf/components/esp_bootloader_format C:/esp/v6.0.1/esp-idf/components/esp_coex C:/esp/v6.0.1/esp-idf/components/esp_common C:/esp/v6.0.1/esp-idf/components/esp_driver_ana_cmpr C:/esp/v6.0.1/esp-idf/components/esp_driver_bitscrambler C:/esp/v6.0.1/esp-idf/components/esp_driver_cam C:/esp/v6.0.1/esp-idf/components/esp_driver_dac C:/esp/v6.0.1/esp-idf/components/esp_driver_dma C:/esp/v6.0.1/esp-idf/components/esp_driver_gpio C:/esp/v6.0.1/esp-idf/components/esp_driver_gptimer C:/esp/v6.0.1/esp-idf/components/esp_driver_i2c C:/esp/v6.0.1/esp-idf/components/esp_driver_i2s C:/esp/v6.0.1/esp-idf/components/esp_driver_i3c C:/esp/v6.0.1/esp-idf/components/esp_driver_isp C:/esp/v6.0.1/esp-idf/components/esp_driver_jpeg C:/esp/v6.0.1/esp-idf/components/esp_driver_ledc C:/esp/v6.0.1/esp-idf/components/esp_driver_mcpwm C:/esp/v6.0.1/esp-idf/components/esp_driver_parlio C:/esp/v6.0.1/esp-idf/components/esp_driver_pcnt C:/esp/v6.0.1/esp-idf/components/esp_driver_ppa C:/esp/v6.0.1/esp-idf/components/esp_driver_rmt C:/esp/v6.0.1/esp-idf/components/esp_driver_sd_intf C:/esp/v6.0.1/esp-idf/components/esp_driver_sdio C:/esp/v6.0.1/esp-idf/components/esp_driver_sdm C:/esp/v6.0.1/esp-idf/components/esp_driver_sdmmc C:/esp/v6.0.1/esp-idf/components/esp_driver_sdspi C:/esp/v6.0.1/esp-idf/components/esp_driver_spi C:/esp/v6.0.1/esp-idf/components/esp_driver_touch_sens C:/esp/v6.0.1/esp-idf/components/esp_driver_tsens C:/esp/v6.0.1/esp-idf/components/esp_driver_twai C:/esp/v6.0.1/esp-idf/components/esp_driver_uart C:/esp/v6.0.1/esp-idf/components/esp_driver_usb_serial_jtag C:/esp/v6.0.1/esp-idf/components/esp_eth C:/esp/v6.0.1/esp-idf/components/esp_event C:/esp/v6.0.1/esp-idf/components/esp_gdbstub C:/esp/v6.0.1/esp-idf/components/esp_hal_ana_cmpr C:/esp/v6.0.1/esp-idf/components/esp_hal_ana_conv C:/esp/v6.0.1/esp-idf/components/esp_hal_cam C:/esp/v6.0.1/esp-idf/components/esp_hal_clock C:/esp/v6.0.1/esp-idf/components/esp_hal_dma C:/esp/v6.0.1/esp-idf/components/esp_hal_gpio C:/esp/v6.0.1/esp-idf/components/esp_hal_gpspi C:/esp/v6.0.1/esp-idf/components/esp_hal_i2c C:/esp/v6.0.1/esp-idf/components/esp_hal_i2s C:/esp/v6.0.1/esp-idf/components/esp_hal_ieee802154 C:/esp/v6.0.1/esp-idf/components/esp_hal_jpeg C:/esp/v6.0.1/esp-idf/components/esp_hal_lcd C:/esp/v6.0.1/esp-idf/components/esp_hal_ledc C:/esp/v6.0.1/esp-idf/components/esp_hal_mcpwm C:/esp/v6.0.1/esp-idf/components/esp_hal_mspi C:/esp/v6.0.1/esp-idf/components/esp_hal_parlio C:/esp/v6.0.1/esp-idf/components/esp_hal_pcnt C:/esp/v6.0.1/esp-idf/components/esp_hal_pmu C:/esp/v6.0.1/esp-idf/components/esp_hal_ppa C:/esp/v6.0.1/esp-idf/components/esp_hal_rmt C:/esp/v6.0.1/esp-idf/components/esp_hal_rtc_timer C:/esp/v6.0.1/esp-idf/components/esp_hal_sd C:/esp/v6.0.1/esp-idf/components/esp_hal_security C:/esp/v6.0.1/esp-idf/components/esp_hal_timg C:/esp/v6.0.1/esp-idf/components/esp_hal_touch_sens C:/esp/v6.0.1/esp-idf/components/esp_hal_twai C:/esp/v6.0.1/esp-idf/components/esp_hal_uart C:/esp/v6.0.1/esp-idf/components/esp_hal_usb C:/esp/v6.0.1/esp-idf/components/esp_hal_wdt C:/esp/v6.0.1/esp-idf/components/esp_hid C:/esp/v6.0.1/esp-idf/components/esp_http_client C:/esp/v6.0.1/esp-idf/components/esp_http_server C:/esp/v6.0.1/esp-idf/components/esp_https_ota C:/esp/v6.0.1/esp-idf/components/esp_https_server C:/esp/v6.0.1/esp-idf/components/esp_hw_support C:/esp/v6.0.1/esp-idf/components/esp_lcd C:/esp/v6.0.1/esp-idf/components/esp_libc C:/esp/v6.0.1/esp-idf/components/esp_local_ctrl C:/esp/v6.0.1/esp-idf/components/esp_mm C:/esp/v6.0.1/esp-idf/components/esp_netif C:/esp/v6.0.1/esp-idf/components/esp_netif_stack C:/esp/v6.0.1/esp-idf/components/esp_partition C:/esp/v6.0.1/esp-idf/components/esp_phy C:/esp/v6.0.1/esp-idf/components/esp_pm C:/esp/v6.0.1/esp-idf/components/esp_psram C:/esp/v6.0.1/esp-idf/components/esp_ringbuf C:/esp/v6.0.1/esp-idf/components/esp_rom C:/esp/v6.0.1/esp-idf/components/esp_security C:/esp/v6.0.1/esp-idf/components/esp_stdio C:/esp/v6.0.1/esp-idf/components/esp_system C:/esp/v6.0.1/esp-idf/components/esp_timer C:/esp/v6.0.1/esp-idf/components/esp_trace C:/esp/v6.0.1/esp-idf/components/esp_usb_cdc_rom_console C:/esp/v6.0.1/esp-idf/components/esp_wifi C:/esp/v6.0.1/esp-idf/components/espcoredump C:/esp/v6.0.1/esp-idf/components/esptool_py C:/esp/v6.0.1/esp-idf/components/fatfs C:/esp/v6.0.1/esp-idf/components/freertos C:/esp/v6.0.1/esp-idf/components/hal C:/esp/v6.0.1/esp-idf/components/heap C:/esp/v6.0.1/esp-idf/components/http_parser C:/esp/v6.0.1/esp-idf/components/idf_test C:/esp/v6.0.1/esp-idf/components/ieee802154 C:/esp/v6.0.1/esp-idf/components/log C:/esp/v6.0.1/esp-idf/components/lwip D:/ESP_S3/main C:/esp/v6.0.1/esp-idf/components/mbedtls C:/esp/v6.0.1/esp-idf/components/nvs_flash C:/esp/v6.0.1/esp-idf/components/nvs_sec_provider C:/esp/v6.0.1/esp-idf/components/openthread C:/esp/v6.0.1/esp-idf/components/partition_table C:/esp/v6.0.1/esp-idf/components/perfmon C:/esp/v6.0.1/esp-idf/components/protobuf-c C:/esp/v6.0.1/esp-idf/components/protocomm C:/esp/v6.0.1/esp-idf/components/pthread C:/esp/v6.0.1/esp-idf/components/rt C:/esp/v6.0.1/esp-idf/components/sdmmc C:/esp/v6.0.1/esp-idf/components/soc C:/esp/v6.0.1/esp-idf/components/spi_flash C:/esp/v6.0.1/esp-idf/components/spiffs C:/esp/v6.0.1/esp-idf/components/tcp_transport C:/esp/v6.0.1/esp-idf/components/ulp C:/esp/v6.0.1/esp-idf/components/unity C:/esp/v6.0.1/esp-idf/components/vfs C:/esp/v6.0.1/esp-idf/components/wear_levelling C:/esp/v6.0.1/esp-idf/components/wpa_supplicant C:/esp/v6.0.1/esp-idf/components/xtensa
-- Configuring done (24.0s)
-- Generating done (2.3s)
-- Build files have been written to: D:/ESP_S3/build

 *  Executing task: C:\Espressif\tools\ninja\1.12.1\ninja.EXE  

[25/1054] Generating ../../partition_table/partition-table.bin
Partition table binary generated. Contents:
*******************************************************************************
# ESP-IDF Partition Table
# Name, Type, SubType, Offset, Size, Flags
nvs,data,nvs,0x9000,24K,
phy_init,data,phy,0xf000,4K,
factory,app,factory,0x10000,1M,
*******************************************************************************
[982/1054] Building C object esp-idf/esp_lcd/CM...s/__idf_esp_lcd.dir/rgb/esp_lcd_panel_rgb.c.obj
FAILED: esp-idf/esp_lcd/CMakeFiles/__idf_esp_lcd.dir/rgb/esp_lcd_panel_rgb.c.obj 
C:\Espressif\tools\xtensa-esp-elf\esp-15.2.0_20251204\xtensa-esp-elf\bin\xtensa-esp32s3-elf-gcc.exe -DESP_PLATFORM -DIDF_VER=\"v6.0.1\" -DSOC_MMU_PAGE_SIZE=CONFIG_MMU_PAGE_SIZE -DSOC_XTAL_FREQ_MHZ=CONFIG_XTAL_FREQ -D_GLIBCXX_HAVE_POSIX_SEMAPHORE -D_GLIBCXX_USE_POSIX_SEMAPHORE -D_GNU_SOURCE -D_POSIX_READER_WRITER_LOCKS -ID:/ESP_S3/build/config -IC:/esp/v6.0.1/esp-idf/components/esp_lcd/include -IC:/esp/v6.0.1/esp-idf/components/esp_lcd/interface -IC:/esp/v6.0.1/esp-idf/components/esp_lcd/rgb/include -IC:/esp/v6.0.1/esp-idf/components/esp_lcd/priv_include -IC:/esp/v6.0.1/esp-idf/components/esp_libc/platform_include -IC:/esp/v6.0.1/esp-idf/components/freertos/config/include -IC:/esp/v6.0.1/esp-idf/components/freertos/config/include/freertos -IC:/esp/v6.0.1/esp-idf/components/freertos/config/xtensa/include -IC:/esp/v6.0.1/esp-idf/components/freertos/FreeRTOS-Kernel/include -IC:/esp/v6.0.1/esp-idf/components/freertos/FreeRTOS-Kernel/portable/xtensa/include -IC:/esp/v6.0.1/esp-idf/components/freertos/FreeRTOS-Kernel/portable/xtensa/include/freertos -IC:/esp/v6.0.1/esp-idf/components/freertos/esp_additions/include -IC:/esp/v6.0.1/esp-idf/components/esp_hw_support/include -IC:/esp/v6.0.1/esp-idf/components/esp_hw_support/include/soc -IC:/esp/v6.0.1/esp-idf/components/esp_hw_support/ldo/include -IC:/esp/v6.0.1/esp-idf/components/esp_hw_support/debug_probe/include -IC:/esp/v6.0.1/esp-idf/components/esp_hw_support/etm/include -IC:/esp/v6.0.1/esp-idf/components/esp_hw_support/mspi_timing_tuning/include -IC:/esp/v6.0.1/esp-idf/components/esp_hw_support/mspi_timing_tuning/tuning_scheme_impl/include -IC:/esp/v6.0.1/esp-idf/components/esp_hw_support/power_supply/include -IC:/esp/v6.0.1/esp-idf/components/esp_hw_support/modem/include -IC:/esp/v6.0.1/esp-idf/components/esp_hw_support/include/soc/esp32s3 -IC:/esp/v6.0.1/esp-idf/components/esp_hw_support/port/esp32s3/. -IC:/esp/v6.0.1/esp-idf/components/esp_hw_support/port/esp32s3/include -IC:/esp/v6.0.1/esp-idf/components/esp_hw_support/mspi_timing_tuning/port/esp32s3/. -IC:/esp/v6.0.1/esp-idf/components/esp_hw_support/mspi_timing_tuning/port/esp32s3/include -IC:/esp/v6.0.1/esp-idf/components/heap/include -IC:/esp/v6.0.1/esp-idf/components/heap/tlsf -IC:/esp/v6.0.1/esp-idf/components/log/include -IC:/esp/v6.0.1/esp-idf/components/soc/include -IC:/esp/v6.0.1/esp-idf/components/soc/esp32s3 -IC:/esp/v6.0.1/esp-idf/components/soc/esp32s3/include -IC:/esp/v6.0.1/esp-idf/components/soc/esp32s3/register -IC:/esp/v6.0.1/esp-idf/components/hal/platform_port/include -IC:/esp/v6.0.1/esp-idf/components/hal/esp32s3/include -IC:/esp/v6.0.1/esp-idf/components/hal/include -IC:/esp/v6.0.1/esp-idf/components/esp_rom/include -IC:/esp/v6.0.1/esp-idf/components/esp_rom/esp32s3/include -IC:/esp/v6.0.1/esp-idf/components/esp_rom/esp32s3/include/esp32s3 -IC:/esp/v6.0.1/esp-idf/components/esp_rom/esp32s3 -IC:/esp/v6.0.1/esp-idf/components/esp_common/include -IC:/esp/v6.0.1/esp-idf/components/esp_system/include -IC:/esp/v6.0.1/esp-idf/components/esp_system/port/soc -IC:/esp/v6.0.1/esp-idf/components/esp_system/port/include/private -IC:/esp/v6.0.1/esp-idf/components/esp_stdio/include -IC:/esp/v6.0.1/esp-idf/components/xtensa/esp32s3/include -IC:/esp/v6.0.1/esp-idf/components/xtensa/include -IC:/esp/v6.0.1/esp-idf/components/xtensa/deprecated_include -IC:/esp/v6.0.1/esp-idf/components/esp_hal_gpio/include -IC:/esp/v6.0.1/esp-idf/components/esp_hal_gpio/esp32s3/include -IC:/esp/v6.0.1/esp-idf/components/esp_hal_usb/include -IC:/esp/v6.0.1/esp-idf/components/esp_hal_usb/esp32s3/include -IC:/esp/v6.0.1/esp-idf/components/esp_hal_pmu/include -IC:/esp/v6.0.1/esp-idf/components/esp_hal_pmu/esp32s3/include -IC:/esp/v6.0.1/esp-idf/components/esp_hal_ana_conv/include -IC:/esp/v6.0.1/esp-idf/components/esp_hal_ana_conv/esp32s3/include -IC:/esp/v6.0.1/esp-idf/components/esp_hal_dma/include -IC:/esp/v6.0.1/esp-idf/components/esp_hal_dma/esp32s3/include -IC:/esp/v6.0.1/esp-idf/components/lwip/include -IC:/esp/v6.0.1/esp-idf/components/lwip/include/apps -IC:/esp/v6.0.1/esp-idf/components/lwip/lwip/src/include -IC:/esp/v6.0.1/esp-idf/components/lwip/port/include -IC:/esp/v6.0.1/esp-idf/components/lwip/port/freertos/include -IC:/esp/v6.0.1/esp-idf/components/lwip/port/esp32xx/include -IC:/esp/v6.0.1/esp-idf/components/lwip/port/esp32xx/include/arch -IC:/esp/v6.0.1/esp-idf/components/lwip/port/esp32xx/include/sys -IC:/esp/v6.0.1/esp-idf/components/esp_driver_gpio/include -IC:/esp/v6.0.1/esp-idf/components/esp_driver_i2c/include -IC:/esp/v6.0.1/esp-idf/components/esp_hal_i2c/esp32s3/include -IC:/esp/v6.0.1/esp-idf/components/esp_hal_i2c/include -IC:/esp/v6.0.1/esp-idf/components/esp_driver_spi/include -IC:/esp/v6.0.1/esp-idf/components/esp_pm/include -IC:/esp/v6.0.1/esp-idf/components/esp_hal_gpspi/include -IC:/esp/v6.0.1/esp-idf/components/esp_hal_gpspi/esp32s3/include -IC:/esp/v6.0.1/esp-idf/components/esp_driver_dma/include -IC:/esp/v6.0.1/esp-idf/components/esp_driver_parlio/include -IC:/esp/v6.0.1/esp-idf/components/esp_hal_parlio/include -IC:/esp/v6.0.1/esp-idf/components/esp_hal_lcd/include -IC:/esp/v6.0.1/esp-idf/components/esp_hal_lcd/esp32s3/include -IC:/esp/v6.0.1/esp-idf/components/esp_mm/include -IC:/esp/v6.0.1/esp-idf/components/esp_psram/include -IC:/esp/v6.0.1/esp-idf/components/esp_psram/xip_impl/include -IC:/esp/v6.0.1/esp-idf/components/esp_driver_i2s/include -IC:/esp/v6.0.1/esp-idf/components/esp_hal_i2s/include -IC:/esp/v6.0.1/esp-idf/components/esp_hal_i2s/esp32s3/include @"D:/ESP_S3/build/toolchain/cflags" -fdiagnostics-color=always -ffunction-sections -fdata-sections -Wall -Werror -Wno-error=unused-function -Wno-error=unused-variable -Wno-error=unused-but-set-variable -Wno-error=deprecated-declarations -Wextra -Wno-error=extra -Wno-unused-parameter -Wno-sign-compare -Wno-enum-conversion -gdwarf-4 -ggdb -Og -fno-shrink-wrap -fmacro-prefix-map=D:/ESP_S3=. -fmacro-prefix-map=C:/esp/v6.0.1/esp-idf=/IDF -fstrict-volatile-bitfields -fno-jump-tables -fno-tree-switch-conversion -std=gnu23 -Wno-old-style-declaration -fzero-init-padding-bits=all -fno-malloc-dce -MD -MT esp-idf/esp_lcd/CMakeFiles/__idf_esp_lcd.dir/rgb/esp_lcd_panel_rgb.c.obj -MF esp-idf\esp_lcd\CMakeFiles\__idf_esp_lcd.dir\rgb\esp_lcd_panel_rgb.c.obj.d -o esp-idf/esp_lcd/CMakeFiles/__idf_esp_lcd.dir/rgb/esp_lcd_panel_rgb.c.obj -c C:/esp/v6.0.1/esp-idf/components/esp_lcd/rgb/esp_lcd_panel_rgb.c
during RTL pass: ira
C:/esp/v6.0.1/esp-idf/components/esp_lcd/rgb/esp_lcd_panel_rgb.c: In function 'rgb_panel_draw_bitmap':
C:/esp/v6.0.1/esp-idf/components/esp_lcd/rgb/esp_lcd_panel_rgb.c:741:1: internal compiler error: Segmentation fault
  741 | }
      | ^
Please submit a full bug report, with preprocessed source (by using -freport-bug).
See <https://gcc.gnu.org/bugs/> for instructions.
[999/1054] Performing configure step for 'bootloader'
-- Found Git: C:/Program Files/Git/cmd/git.exe (found version "2.54.0.windows.1")
-- Component directory C:/esp/v6.0.1/esp-idf/components/mqtt does not contain a CMakeLists.txt file. No component will be added
-- Minimal build - OFF
-- The C compiler identification is GNU 15.2.0
-- The CXX compiler identification is GNU 15.2.0
-- The ASM compiler identification is GNU
-- Found assembler: C:/Espressif/tools/xtensa-esp-elf/esp-15.2.0_20251204/xtensa-esp-elf/bin/xtensa-esp32s3-elf-gcc.exe
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working C compiler: C:/Espressif/tools/xtensa-esp-elf/esp-15.2.0_20251204/xtensa-esp-elf/bin/xtensa-esp32s3-elf-gcc.exe - skipped
-- Detecting C compile features
-- Detecting C compile features - done
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Check for working CXX compiler: C:/Espressif/tools/xtensa-esp-elf/esp-15.2.0_20251204/xtensa-esp-elf/bin/xtensa-esp32s3-elf-g++.exe - skipped
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Building ESP-IDF components for target esp32s3
-- ESP-TEE is currently supported only on the esp32c6;esp32h2;esp32c5;esp32c61 SoCs
-- KCONFIG_REPORT_VERBOSITY not set, using default
-- Project sdkconfig file D:/ESP_S3/sdkconfig
Configuration Report               
+---------------------------------+
|  Parser Version: 1              |
|  Verbosity: default             |
|  Defaults policy: sdkconfig     |
|  Status: Finished successfully  |
|                                 |
+---------------------------------+
-- Compiler supported targets: xtensa-esp-elf
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/soc/esp32s3/ld/esp32s3.peripherals.ld
-- Bootloader project name: "bootloader" version: 1
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_hal_wdt/esp32s3/rom.wdt.ld
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_rom/esp32s3/ld/esp32s3.rom.ld
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_rom/esp32s3/ld/esp32s3.rom.api.ld
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_rom/esp32s3/ld/esp32s3.rom.bt_funcs.ld
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_rom/esp32s3/ld/esp32s3.rom.libgcc.ld
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_rom/esp32s3/ld/esp32s3.rom.version.ld
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/esp_rom/esp32s3/ld/esp32s3.rom.libc.ld
-- Components: bootloader bootloader_support efuse esp_app_format esp_blockdev esp_bootloader_format esp_common esp_hal_ana_conv esp_hal_clock esp_hal_dma esp_hal_gpio esp_hal_gpspi esp_hal_mspi esp_hal_pmu esp_hal_rtc_timer esp_hal_security esp_hal_timg esp_hal_uart esp_hal_usb esp_hal_wdt esp_hw_support esp_libc esp_rom esp_security esp_stdio esp_system esptool_py freertos hal log main micro-ecc partition_table soc spi_flash xtensa
-- Component paths: C:/esp/v6.0.1/esp-idf/components/bootloader C:/esp/v6.0.1/esp-idf/components/bootloader_support C:/esp/v6.0.1/esp-idf/components/efuse C:/esp/v6.0.1/esp-idf/components/esp_app_format C:/esp/v6.0.1/esp-idf/components/esp_blockdev C:/esp/v6.0.1/esp-idf/components/esp_bootloader_format C:/esp/v6.0.1/esp-idf/components/esp_common C:/esp/v6.0.1/esp-idf/components/esp_hal_ana_conv C:/esp/v6.0.1/esp-idf/components/esp_hal_clock C:/esp/v6.0.1/esp-idf/components/esp_hal_dma C:/esp/v6.0.1/esp-idf/components/esp_hal_gpio C:/esp/v6.0.1/esp-idf/components/esp_hal_gpspi C:/esp/v6.0.1/esp-idf/components/esp_hal_mspi C:/esp/v6.0.1/esp-idf/components/esp_hal_pmu C:/esp/v6.0.1/esp-idf/components/esp_hal_rtc_timer C:/esp/v6.0.1/esp-idf/components/esp_hal_security C:/esp/v6.0.1/esp-idf/components/esp_hal_timg C:/esp/v6.0.1/esp-idf/components/esp_hal_uart C:/esp/v6.0.1/esp-idf/components/esp_hal_usb C:/esp/v6.0.1/esp-idf/components/esp_hal_wdt C:/esp/v6.0.1/esp-idf/components/esp_hw_support C:/esp/v6.0.1/esp-idf/components/esp_libc C:/esp/v6.0.1/esp-idf/components/esp_rom C:/esp/v6.0.1/esp-idf/components/esp_security C:/esp/v6.0.1/esp-idf/components/esp_stdio C:/esp/v6.0.1/esp-idf/components/esp_system C:/esp/v6.0.1/esp-idf/components/esptool_py C:/esp/v6.0.1/esp-idf/components/freertos C:/esp/v6.0.1/esp-idf/components/hal C:/esp/v6.0.1/esp-idf/components/log C:/esp/v6.0.1/esp-idf/components/bootloader/subproject/main C:/esp/v6.0.1/esp-idf/components/bootloader/subproject/components/micro-ecc C:/esp/v6.0.1/esp-idf/components/partition_table C:/esp/v6.0.1/esp-idf/components/soc C:/esp/v6.0.1/esp-idf/components/spi_flash C:/esp/v6.0.1/esp-idf/components/xtensa
-- Adding linker script C:/esp/v6.0.1/esp-idf/components/bootloader/subproject/main/ld/esp32s3/bootloader.ld.in
--   -> Preprocessing .in script: C:/esp/v6.0.1/esp-idf/components/bootloader/subproject/main/ld/esp32s3/bootloader.ld.in
-- Configuring done (24.8s)
-- Generating done (0.3s)
-- Build files have been written to: D:/ESP_S3/build/bootloader
ninja: build stopped: subcommand failed.

 *  The terminal process "C:\Espressif\tools\ninja\1.12.1\ninja.EXE" terminated with exit code: 1. 
