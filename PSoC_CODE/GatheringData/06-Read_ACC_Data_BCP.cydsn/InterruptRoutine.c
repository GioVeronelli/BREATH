
#include "InterruptRoutine.h"


int16_t OutData;
uint8_t Acc_Data[2];
uint8_t ZYX_DA;
uint8_t ZYX_OR;
uint8_t status_reg;
float g = 9.81;
char ch_received;
char start_stream;

CY_ISR(Custom_ISR_RX)
{
    ch_received = UART_1_GetChar(); 
    switch(ch_received)
    {
        case 's':
            PWM_LED_Stop();
            LED_G_Write(HIGH);
            LED_B_Write(LOW);
            BUZZER_Write(LOW);
            start_stream=1;
            break;
        
        case 'v':
            LED_G_Write(LOW);
            LED_B_Write(HIGH);
            BUZZER_Write(LOW);
            start_stream=0;
            break;
            
        case 'b':
            BUZZER_Write(HIGH);
            PWM_LED_Start();
            LED_G_Write(LOW);
            LED_B_Write(LOW);
            break;

        case 't':
            LED_B_Write(HIGH);
            PWM_LED_Stop();
            BUZZER_Write(LOW);
            LED_G_Write(LOW);
            break;
            
        case 'o':
            LED_B_Write(LOW);
            LED_R_Write(LOW);
            BUZZER_Write(LOW);
            LED_G_Write(HIGH);
            break;
            
        case 'd':
            PWM_LED_Start();
            LED_G_Write(LOW);
            LED_B_Write(LOW);
            BUZZER_Write(LOW);
            break;
                
    }
}        
        
CY_ISR(Custom_ISR_Data)
{
    
    ErrorCode error = I2C_Peripheral_UReadRegister(LIS3DH_DEVICE_ADDRESS,LIS3DH_STATUS_REG,&status_reg);
    
    if (error == NO_ERROR)
    { 
        ZYX_DA = status_reg & (0b00001000); 
        ZYX_OR = status_reg &  (0b10000000);
 
        if(ZYX_DA == LIS3DH_STATUS_REG_ZYX_DA_1)
        {
            error = I2C_Peripheral_UReadRegister(LIS3DH_DEVICE_ADDRESS,LIS3DH_OUT_Z_L,&Acc_Data[0]);
            error = I2C_Peripheral_UReadRegister(LIS3DH_DEVICE_ADDRESS,LIS3DH_OUT_Z_H,&Acc_Data[1]);
            
            if(error == NO_ERROR)
            {
                DataBuffer[1]=Acc_Data[0];
                DataBuffer[2]=Acc_Data[1];
                if(start_stream)
                {
                    UART_1_PutArray(DataBuffer,TRANSMIT_DATA_BUFFER_SIZE);
                }
            }
            else
            {
                UART_1_PutString("Errore");
            }
        }       
    }
}


