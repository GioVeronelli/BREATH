# THIS FILE IS AUTOMATICALLY GENERATED
<<<<<<< HEAD
# Project: C:\Users\Giovanni\Desktop\AY2324_II_Project-1\PSoC_CODE\GatheringData\06-Read_ACC_Data_BCP.cydsn\Read_Acc_Data_XYZ.cydsn\Read_Acc_Data_XYZ.cyprj
# Date: Wed, 17 Jul 2024 16:25:22 GMT
=======
# Project: C:\Users\robed\OneDrive - Politecnico di Milano\Desktop\Polimi\2_Anno\2_Semestre\Electronic Lab\PROJECT\PSoC_CODE\GatheringData\06-Read_ACC_Data_BCP.cydsn\Read_Acc_Data_XYZ.cydsn\Read_Acc_Data_XYZ.cyprj
# Date: Wed, 17 Jul 2024 15:56:30 GMT
>>>>>>> a1b7d34d802777230a6730c25fd6374a5ddf179e
#set_units -time ns
create_clock -name {CyILO} -period 1000000 -waveform {0 500000} [list [get_pins {ClockBlock/ilo}] [get_pins {ClockBlock/clk_100k}] [get_pins {ClockBlock/clk_1k}] [get_pins {ClockBlock/clk_32k}]]
create_clock -name {CyIMO} -period 333.33333333333331 -waveform {0 166.666666666667} [list [get_pins {ClockBlock/imo}]]
create_clock -name {CyPLL_OUT} -period 41.666666666666664 -waveform {0 20.8333333333333} [list [get_pins {ClockBlock/pllout}]]
create_clock -name {CyMASTER_CLK} -period 41.666666666666664 -waveform {0 20.8333333333333} [list [get_pins {ClockBlock/clk_sync}]]
create_generated_clock -name {CyBUS_CLK} -source [get_pins {ClockBlock/clk_sync}] -edges {1 2 3} [list [get_pins {ClockBlock/clk_bus_glb}]]
create_generated_clock -name {UART_1_IntClock} -source [get_pins {ClockBlock/clk_sync}] -edges {1 313 627} [list [get_pins {ClockBlock/dclk_glb_0}]]
create_generated_clock -name {CLOCK_LED_PWM} -source [get_pins {ClockBlock/clk_sync}] -edges {1 240001 480001} [list [get_pins {ClockBlock/dclk_glb_1}]]


<<<<<<< HEAD
# Component constraints for C:\Users\Giovanni\Desktop\AY2324_II_Project-1\PSoC_CODE\GatheringData\06-Read_ACC_Data_BCP.cydsn\Read_Acc_Data_XYZ.cydsn\TopDesign\TopDesign.cysch
# Project: C:\Users\Giovanni\Desktop\AY2324_II_Project-1\PSoC_CODE\GatheringData\06-Read_ACC_Data_BCP.cydsn\Read_Acc_Data_XYZ.cydsn\Read_Acc_Data_XYZ.cyprj
# Date: Wed, 17 Jul 2024 16:25:13 GMT
=======
# Component constraints for C:\Users\robed\OneDrive - Politecnico di Milano\Desktop\Polimi\2_Anno\2_Semestre\Electronic Lab\PROJECT\PSoC_CODE\GatheringData\06-Read_ACC_Data_BCP.cydsn\Read_Acc_Data_XYZ.cydsn\TopDesign\TopDesign.cysch
# Project: C:\Users\robed\OneDrive - Politecnico di Milano\Desktop\Polimi\2_Anno\2_Semestre\Electronic Lab\PROJECT\PSoC_CODE\GatheringData\06-Read_ACC_Data_BCP.cydsn\Read_Acc_Data_XYZ.cydsn\Read_Acc_Data_XYZ.cyprj
# Date: Wed, 17 Jul 2024 15:56:26 GMT
>>>>>>> a1b7d34d802777230a6730c25fd6374a5ddf179e
