
#include "InterruptRoutines.h"
int16_t OutData;
uint8_t Acc_Data[2];
uint8_t ZYX_DA;
uint8_t ZYX_OR;
uint8_t status_reg;
float g = 9.81;
char ch_received;


CY_ISR(Custom_ISR_RX)
{
    ch_received = UART_1_GetChar(); 
    switch(ch_received)
    {
        case 's':
            PWM_LED_Stop();
            LED_G_Write(LOW);
            LED_B_Write(HIGH);
            BUZZER_Write(LOW);
            start_stream=1;
            break;
        
        case 'v':
            PWM_LED_Start();
            LED_G_Write(LOW);
            LED_B_Write(LOW);
            BUZZER_Write(LOW);
            start_stream=0;
            break;
            
        case 'b':
            BUZZER_Write(HIGH);
            LED_G_Write(HIGH);
            LED_B_Write(LOW);
            break;

        case 'o':
            BUZZER_Write(LOW);
            LED_G_Write(LOW);
            LED_B_Write(HIGH);
            break;
                
    }
}        





CY_ISR(Custom_ISR_Data)
{
    
    ErrorCode error = I2C_Peripheral_UReadRegister(LIS3DH_DEVICE_ADDRESS,
                                                   LIS3DH_STATUS_REG,
                                                   &status_reg);
    if (error == NO_ERROR)
    { 
        ZYX_DA = status_reg & (0b00001000); 
        ZYX_OR = status_reg &  (0b10000000);
 
        if(ZYX_DA == LIS3DH_STATUS_REG_ZYX_DA_1)
        {
            ErrorCode error = I2C_Peripheral_ReadRegisterMulti(LIS3DH_DEVICE_ADDRESS,
                                                               LIS3DH_OUT_X_L, 
                                                               DATA_BUFFER_SIZE-2,
                                                               &DataStream_XYZ[1]);        
                 
            if(error == NO_ERROR)
            {
                DataStream_XYZ[0] = 0xA0;
                DataStream_XYZ[DATA_BUFFER_SIZE-1] = 0xC0;
                UART_1_PutArray(DataStream_XYZ, DATA_BUFFER_SIZE);      
            }
            else
            {
                UART_1_PutString("Errore");
            }
        }       
    }
}
