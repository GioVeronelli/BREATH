/* ========================================
 *
 * Copyright YOUR COMPANY, THE YEAR
 * All Rights Reserved
 * UNPUBLISHED, LICENSED SOFTWARE.
 *
 * CONFIDENTIAL AND PROPRIETARY INFORMATION
 * WHICH IS THE PROPERTY OF your company.
 *
 * ========================================
*/
#include <stdio.h>
#include "project.h"
#include "I2C_Interface.h"
#include "LIS3DH.h"
#include "InterruptRoutine.h"

// Set this to 1 to send byte data for the Bridge Control Panel
// Otherwise set it to 0 to send temperature data as int16_t
#define USE_BRIDGECONTROLPANEL  0

int main(void)
{
    CyGlobalIntEnable; /* Enable global interrupts. */

    /* Place your initialization/startup code here (e.g. MyInst_Start()) */
    I2C_Peripheral_Start();
    UART_1_Start();
    isr_STREAM_StartEx(Custom_ISR_RX);
    CyDelay(5); //"The boot procedure is complete about 5 ms after device power-up."
    DataBuffer[0]=0xA0;
    DataBuffer[TRANSMIT_DATA_BUFFER_SIZE-1]=0xC0;
    PWM_LED_Start();
    
    // Check if LIS3DH is connected
    uint32_t rval = I2C_Master_MasterSendStart(LIS3DH_DEVICE_ADDRESS, I2C_Master_WRITE_XFER_MODE);
    if( rval == I2C_Master_MSTR_NO_ERROR ) 
    {
        UART_1_PutString("LIS3DH found @ address 0x18\r\n");
    }
    
    I2C_Master_MasterSendStop();
    
    // String to print out messages over UART
    char message[50] = {'\0'};
    
    UART_1_PutString("**************\r\n");
    UART_1_PutString("** I2C Scan **\r\n");
    UART_1_PutString("**************\r\n");
    
    CyDelay(10);
    
    // Setup the screen and print the header
	UART_1_PutString("\n\n   ");
	for(uint8_t i = 0; i<0x10; i++)
	{
        sprintf(message, "%02X ", i);
		UART_1_PutString(message);
	}
    
    // SCAN the I2C BUS for slaves
	for( uint8_t i2caddress = 0; i2caddress < 0x80; i2caddress++ ) {
        
		if(i2caddress % 0x10 == 0 ) {
            sprintf(message, "\n%02X ", i2caddress);
		    UART_1_PutString(message);
        }
 
		rval = I2C_Master_MasterSendStart(i2caddress, I2C_Master_WRITE_XFER_MODE);
        
        if( rval == I2C_Master_MSTR_NO_ERROR ) // If you get ACK then print the address
		{
            sprintf(message, "%02X ", i2caddress);
		    UART_1_PutString(message);
		}
		else //  Otherwise print a --
		{
		    UART_1_PutString("-- ");
		}
        I2C_Master_MasterSendStop();
	}
	UART_1_PutString("\n\n");
    
    
    
    
    
    /******************************************/
    /*            I2C Accelerometer                 */
    /******************************************/
    // SET INTERRUPT ON CONTROL_REGISTER_3
    uint8_t ctrl_reg3;
    ErrorCode error = I2C_Peripheral_UReadRegister(LIS3DH_DEVICE_ADDRESS,
                                                   LIS3DH_CTRL_REG3,
                                                   &ctrl_reg3);
    if( error == NO_ERROR ) 
    {
        sprintf(message, "CTRL register 3 value: 0x%02X\r\n", ctrl_reg3);
        UART_1_PutString(message);
    }
    else 
    {
        UART_1_PutString("I2C error while reading LIS3DH_CTRL_REG1\r\n");
    }
    
    if(ctrl_reg3 != LIS3DH_CTRL_REG3_ENABLE_INT)
    {
        ctrl_reg3 = LIS3DH_CTRL_REG3_ENABLE_INT;
        error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,
                                             LIS3DH_CTRL_REG3,
                                             ctrl_reg3); 
         if (error == NO_ERROR)
        {
            sprintf(message, "\r\nCTRL register 3 successfully written as: 0x%02X\r\n", ctrl_reg3);
            UART_1_PutString(message);
        }
        else
        {
            UART_1_PutString("\r\nError occured during I2C comm to set control register 3\r\n");
        }
    }
    

    
    
    
    
    //SET DEL CONTROL_REGISTER_1: ENABLE Z AXIS AND ODR:200HZ
    uint8_t ctrl_reg1;
    error = I2C_Peripheral_UReadRegister(LIS3DH_DEVICE_ADDRESS,LIS3DH_CTRL_REG1,&ctrl_reg1);
    
    if( error == NO_ERROR ) 
    {
        sprintf(message, "CTRL register 1 value: 0x%02X\r\n", ctrl_reg1);
        UART_1_PutString(message);
    }
    else 
    {
        UART_1_PutString("I2C error while reading LIS3DH_CTRL_REG1\r\n");
    }
    
    if(ctrl_reg1 != LIS3DH_NORMAL_MODE_CTRL_REG1_200_Z)
    {
        ctrl_reg1 = LIS3DH_NORMAL_MODE_CTRL_REG1_200_Z;
        error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,LIS3DH_CTRL_REG1,ctrl_reg1); 
        if (error == NO_ERROR)
        {
            sprintf(message, "\r\nCTRL register 1 successfully written as: 0x%02X\r\n", ctrl_reg1);
            UART_1_PutString(message);
        }
        else
        {
            UART_1_PutString("\r\nError occured during I2C comm to set control register 1\r\n");
        }
    }
    
    
    //SET DEL CONTROL_REGISTER_4: MODALITY: HR, BDU:ACTIVE, FS= +-2g
    uint8_t ctrl_reg4;
    error = I2C_Peripheral_UReadRegister(LIS3DH_DEVICE_ADDRESS,
                                         LIS3DH_CTRL_REG4,
                                         &ctrl_reg4);
    if( error == NO_ERROR ) {
        sprintf(message, "CTRL register 4 value: 0x%02X\r\n", ctrl_reg4);
        UART_1_PutString(message);
    }
    else {
        UART_1_PutString("I2C error while reading LIS3DH_CTRL_REG4\r\n");
    }
    
    if(ctrl_reg4 != LIS3DH_CTRL_REG4_BDU_ACTIVE_HR)
    {
        ctrl_reg4 = LIS3DH_CTRL_REG4_BDU_ACTIVE_HR;
        error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,LIS3DH_CTRL_REG4,ctrl_reg4);
        
        if (error == NO_ERROR)
        {
            sprintf(message, "\r\nCTRL register 4 successfully written as: 0x%02X\r\n", ctrl_reg4);
            UART_1_PutString(message);
        }
        else
        {
            UART_1_PutString("\r\nError occured during I2C comm to set control register 1\r\n");
        }
    }
    
    
    
    
    uint8_t ctrl_reg5;
    error = I2C_Peripheral_UReadRegister(LIS3DH_DEVICE_ADDRESS,
                                         LIS3DH_CTRL_REG5,
                                         &ctrl_reg5);
    if( error == NO_ERROR ) {
        sprintf(message, "CTRL register 5 value: 0x%02X\r\n", ctrl_reg5);
        UART_1_PutString(message);
    }
    else {
        UART_1_PutString("I2C error while reading LIS3DH_CTRL_REG5\r\n");
    }
    
    if(ctrl_reg5 != 0x00)
    {
        ctrl_reg5 = 0x00;
        error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,LIS3DH_CTRL_REG5,ctrl_reg5);
        
        if (error == NO_ERROR)
        {
            sprintf(message, "\r\nCTRL register 5 successfully written as: 0x%02X\r\n", ctrl_reg5);
            UART_1_PutString(message);
        }
        else
        {
            UART_1_PutString("\r\nError occured during I2C comm to set control register 5\r\n");
        }
    }
    
    
    uint8_t ctrl_reg6;
    error = I2C_Peripheral_UReadRegister(LIS3DH_DEVICE_ADDRESS,
                                         LIS3DH_CTRL_REG6,
                                         &ctrl_reg6);
    if( error == NO_ERROR ) {
        sprintf(message, "CTRL register 6 value: 0x%02X\r\n", ctrl_reg6);
        UART_1_PutString(message);
    }
    else {
        UART_1_PutString("I2C error while reading LIS3DH_CTRL_REG6\r\n");
    }
    
    if(ctrl_reg6 != 0x00)
    {
        ctrl_reg6 = 0x00;
        error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,LIS3DH_CTRL_REG6,ctrl_reg6);
        
        if (error == NO_ERROR)
        {
            sprintf(message, "\r\nCTRL register 6 successfully written as: 0x%02X\r\n", ctrl_reg6);
            UART_1_PutString(message);
        }
        else
        {
            UART_1_PutString("\r\nError occured during I2C comm to set control register 6\r\n");
        }
    }
    
    uint8_t status_reg;
    error = I2C_Peripheral_UReadRegister(LIS3DH_DEVICE_ADDRESS,
                                         LIS3DH_STATUS_REG,
                                         &status_reg);
    
    
    if( error == NO_ERROR ) {
        sprintf(message, "CTRL status_reg: 0x%02X\r\n",status_reg);
        UART_1_PutString(message);
    }
    else {
        UART_1_PutString("I2C error while reading status_reg\r\n");
    }
    
    isr_DATA_StartEx(Custom_ISR_Data);
    
    
   
    for(;;)
    { 
        Pin_INT_ClearInterrupt();
    }
}   


/* [] END OF FILE */
