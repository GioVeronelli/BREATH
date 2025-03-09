#ifndef __INTERRUPT_ROUTINE_H
    #define __INTERRUPT_ROUTINE_H
    #include "cytypes.h"
    #include "LIS3DH.h"
    #include "I2C_Interface.h"
    #include "project.h"
    #include "stdio.h"
    
    
    #define DATA_BUFFER_SIZE 8 
    #define HIGH 1
    #define LOW 0
    CY_ISR_PROTO(Custom_ISR_RX);
    CY_ISR_PROTO(Custom_ISR_Data);
    
    uint8_t DataStream_XYZ[DATA_BUFFER_SIZE];
   
    
#endif