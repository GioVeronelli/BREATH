

#ifndef __INTERRUPT_ROUTINE_H
    #define __INTERRUPT_ROUTINE_H
    #include "cytypes.h"
    #include "LIS3DH.h"
    #include "I2C_Interface.h"
    #include "project.h"
    #include "stdio.h"
    
    
    #define BYTE_TO_SEND 2
    #define TRANSMIT_DATA_BUFFER_SIZE 1+BYTE_TO_SEND+1 
    #define HIGH 1
    #define LOW 0
    CY_ISR_PROTO(Custom_ISR_Data);
    CY_ISR_PROTO(Custom_ISR_RX);
    
    uint8 DataBuffer[TRANSMIT_DATA_BUFFER_SIZE];
   
    
#endif

/* [] END OF FILE */
