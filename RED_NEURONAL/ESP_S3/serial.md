En línea: 1 Carácter: 1
+ }
+ ~
Token '}' inesperado en la expresión o la instrucción.
    + CategoryInfo          : ParserError: (:) [], ParentContainsErrorRecordException
    + FullyQualifiedErrorId : UnexpectedToken
 
PS D:\ESP_S3> }
En línea: 1 Carácter: 1
+ }
+ ~
Token '}' inesperado en la expresión o la instrucción.
    + CategoryInfo          : ParserError: (:) [], ParentContainsErrorRecordException
    + FullyQualifiedErrorId : UnexpectedToken
 
PS D:\ESP_S3> $env:IDF_PATH = 'C:/esp/v5.3.5/frameworks/esp-idf-v5.3.5/';
PS D:\ESP_S3>  & 'C:\esp\v5.3.5\python_env\idf5.3_py3.11_env\Scripts\python.exe' 'C:\esp\v5.3.5\frameworks\esp-idf-v5.3.5\tools\idf_monitor.py' -p COM6 -b 115200 --toolchain-prefix xtensa-esp32s3-elf- --make '''C:\esp\v5.3.5\python_env\idf5.3_py3.11_env\Scripts\python.exe'' ''C:\esp\v5.3.5\frameworks\esp-idf-v5.3.5\tools\idf.py''' --target esp32s3 'd:\ESP_S3\build\wifi_verificacion.elf'
--- Warning: GDB cannot open serial ports accessed as COMx
--- Using \\.\COM6 instead...
--- esp-idf-monitor 1.9.0 on \\.\COM6 115200
--- Quit: Ctrl+] | Menu: Ctrl+T | Help: Ctrl+T followed by Ctrl+H
ESP-ROM:esp32s3-20210327
Build:Mar 27 2021
rst:0x15 (USB_UART_CHIP_RESET),boot:0x8 (SPI_FAST_FLASH_BOOT)
Saved PC:0x4037ad72
--- 0x4037ad72: esp_cpu_wait_for_intr at C:/esp/v5.3.5/frameworks/esp-idf-v5.3.5/components/esp_hw_support/cpu.c:64
SPIWP:0xee
mode:DIO, clock div:1
load:0x3fce2810,len:0x1828
load:0x403c8700,len:0x4
load:0x403c8704,len:0xce8
load:0x403cb700,len:0x2eb8
entry 0x403c8918
I (26) boot: ESP-IDF v5.3.5 2nd stage bootloader
I (27) boot: compile time Jun 16 2026 00:52:18
I (27) boot: Multicore bootloader
I (30) boot: chip revision: v0.2
I (33) boot: efuse block revision: v1.3
I (38) boot.esp32s3: Boot SPI Speed : 80MHz
I (43) boot.esp32s3: SPI Mode       : DIO
I (48) boot.esp32s3: SPI Flash Size : 2MB
I (52) boot: Enabling RNG early entropy source...
I (58) boot: Partition Table:
I (61) boot: ## Label            Usage          Type ST Offset   Length
I (69) boot:  0 nvs              WiFi data        01 02 00009000 00006000
I (76) boot:  1 phy_init         RF data          01 01 0000f000 00001000
I (83) boot:  2 factory          factory app      00 00 00010000 00100000
I (91) boot: End of partition table
I (95) esp_image: segment 0: paddr=00010020 vaddr=3c070020 size=16d88h ( 93576) map
I (121) esp_image: segment 1: paddr=00026db0 vaddr=3fc9a200 size=04e90h ( 20112) load
I (125) esp_image: segment 2: paddr=0002bc48 vaddr=40374000 size=043d0h ( 17360) load
I (130) esp_image: segment 3: paddr=00030020 vaddr=42000020 size=6e828h (452648) map
I (218) esp_image: segment 4: paddr=0009e850 vaddr=403783d0 size=11d58h ( 73048) load
I (243) boot: Loaded app from partition at offset 0x10000
I (243) boot: Disabling RNG early entropy source...
I (255) cpu_start: Multicore app
I (264) cpu_start: Pro cpu start user code
I (264) cpu_start: cpu freq: 160000000 Hz
I (265) app_init: Application information:
I (267) app_init: Project name:     wifi_verificacion
I (273) app_init: App version:      1
I (277) app_init: Compile time:     Jun 16 2026 00:51:58
I (283) app_init: ELF file SHA256:  ab21aac42...
I (289) app_init: ESP-IDF:          v5.3.5
I (293) efuse_init: Min chip rev:     v0.0
I (298) efuse_init: Max chip rev:     v0.99 
I (303) efuse_init: Chip rev:         v0.2
I (308) heap_init: Initializing. RAM available for dynamic allocation:
I (315) heap_init: At 3FCA2B98 len 00046B78 (282 KiB): RAM
I (321) heap_init: At 3FCE9710 len 00005724 (21 KiB): RAM
I (327) heap_init: At 3FCF0000 len 00008000 (32 KiB): DRAM
I (334) heap_init: At 600FE000 len 00001FE8 (7 KiB): RTCRAM
I (341) spi_flash: detected chip: boya
I (344) spi_flash: flash io: dio
W (348) spi_flash: Detected size(16384k) larger than the size in the binary image header(2048k). Using the size in the binary image header.
I (362) sleep: Configure to isolate all GPIO pins in sleep state
I (368) sleep: Enable automatic switching of GPIO sleep configuration
I (376) main_task: Started on CPU0
I (386) main_task: Calling app_main()
I (416) pp: pp rom version: e7ae62f
I (416) net80211: net80211 rom version: e7ae62f
I (436) wifi:wifi driver task: 3fcac47c, prio:23, stack:3584, core=0
I (446) wifi:wifi firmware version: 18db208
I (446) wifi:wifi certification version: v7.0
I (446) wifi:config NVS flash: enabled
I (446) wifi:config nano formating: disabled
I (446) wifi:Init data frame dynamic rx buffer num: 32
I (456) wifi:Init static rx mgmt buffer num: 5
I (456) wifi:Init management short buffer num: 32
I (466) wifi:Init dynamic tx buffer num: 32
I (466) wifi:Init static tx FG buffer num: 2
I (466) wifi:Init static rx buffer size: 1600
I (476) wifi:Init static rx buffer num: 10
I (476) wifi:Init dynamic rx buffer num: 32
I (486) wifi_init: rx ba win: 6
I (486) wifi_init: accept mbox: 6
I (486) wifi_init: tcpip mbox: 32
I (496) wifi_init: udp mbox: 6
I (496) wifi_init: tcp mbox: 6
I (506) wifi_init: tcp tx win: 5760
I (506) wifi_init: tcp rx win: 5760
I (506) wifi_init: tcp mss: 1440
I (516) wifi_init: WiFi IRAM OP enabled
I (516) wifi_init: WiFi RX IRAM OP enabled
I (526) phy_init: phy_version 711,97bcf0a2,Aug 25 2025,19:04:10
I (566) wifi:mode : sta (30:ed:a0:bb:3d:60)
I (566) wifi:enable tsf
I (576) wifi:Set ps type: 0, coexist: 0

I (576) wifi: Conectando a 'OPPOA805G'...
W (2986) wifi: Desconectado, reason=201
W (5396) wifi: Desconectado, reason=201
W (7806) wifi: Desconectado, reason=201
I (7896) wifi:new:<1,0>, old:<1,0>, ap:<255,255>, sta:<1,0>, prof:1, snd_ch_cfg:0x0
I (7896) wifi:state: init -> auth (0xb0)
I (7946) wifi:state: auth -> assoc (0x0)
I (8946) wifi:state: assoc -> init (0x400)
I (8956) wifi:new:<1,0>, old:<1,0>, ap:<255,255>, sta:<1,0>, prof:1, snd_ch_cfg:0x0
W (8956) wifi: Desconectado, reason=4
W (11366) wifi: Desconectado, reason=205
I (11446) wifi:new:<1,0>, old:<1,0>, ap:<255,255>, sta:<1,0>, prof:1, snd_ch_cfg:0x0
I (11446) wifi:state: init -> auth (0xb0)
I (12456) wifi:state: auth -> init (0x200)
I (12466) wifi:new:<1,0>, old:<1,0>, ap:<255,255>, sta:<1,0>, prof:1, snd_ch_cfg:0x0
W (12466) wifi: Desconectado, reason=2
E (12466) wifi: No se pudo conectar a 'OPPOA805G'
I (12466) main_task: Returned from app_main()
