# Raspberry Pi Scale-Balance
Balance de cuisine avec afficheur / kitchen scale with display 

Uses :
- 4x 5 Kg weight sensors (Aliexpress)
- 1x HX711 24 bit ADC converter breakboard (Aliexpress)
- 1x 128x64 monochom Oled display based on SH1106 driver (ebay)
- 1x Raspberry Pi 2 Model B Revision 1.1 1GB + SD card + power supply

Scripts runs on Python3 (not tested on Python2 but should work).
No external lib required, based on Raspbian Strech version dated November 13th 2018.

Once launched, display a 'splash screen' for 1 second (8TN.png) then display measured value.

Zero settings and scale ratio are done through cal_zero and cal_1kg variables (depends on each set of the sensors).
Sevral reading are averaged to get almost a gram stable reading (variable avgnr).

Empirical values are filtered out based on specific values and when measures took too long (very likely related to the fact that the bit banging is not time accurate due to Linux OS, this is likely to be fixed with proper SPI specific lib usage, ... but works good for my usage like that...!).
