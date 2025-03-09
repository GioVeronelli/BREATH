
#ifndef __LIS3DH_H
    #define __LIS3DH_H

    /**
    *   \brief 7-bit I2C address of the slave device.
    */
    #define LIS3DH_DEVICE_ADDRESS 0x18
    

    /**
    *   \brief Address of the WHO AM I register
    */
    #define LIS3DH_WHO_AM_I_REG_ADDR 0x0F
    
    /**
    *   \brief WHOAMI return value
    */
    #define LIS3DH_WHOAMI_RETVAL     0x33

    /**
    *   \brief Address of the Status register
    */
    #define LIS3DH_STATUS_REG 0x27
    

    /**
    *   \brief Address of the CTRL_REG1
    */
   
    #define LIS3DH_CTRL_REG1 0x20
    #define LIS3DH_CTRL_REG1_100HZ_XYZ 0x57
    #define LIS3DH_NORMAL_MODE_CTRL_REG1_200_Z 0x64
    #define LIS3DH_NORMAL_MODE_CTRL_REG1_200_XYZ 0x67
    /**
    *   \brief Address of the CTRL_REG2
    */
    #define LIS3DH_CTRL_REG2 0x21
    /**
    *   \brief Address of the CTRL_REG3
    */
    #define LIS3DH_CTRL_REG3 0x22
    #define LIS3DH_CTRL_REG3_OVRINT_EN 0x02
    #define LIS3DH_CTRL_REG3_ENABLE_INT 0x10
    /**
    *   \brief Address of the CTRL_REG4
    */
    #define LIS3DH_CTRL_REG4 0x23
    #define LIS3DH_CTRL_REG4_BDU_ACTIVE_HR 0x80
    /**
    *   \brief Address of the CTRL_REG5
    */
    #define LIS3DH_CTRL_REG5 0x24
    #define LIS3DH_CTRL_REG5_FIFO_EN 0x40
    /**
    *   \brief Address of the CTRL_REG6
    */
    #define LIS3DH_CTRL_REG6 0x25

   
    /**
    *   \brief Address of the FIFO
    */
    #define FIFO_CTRL_REG 0x2E
    #define FIFO_STREAM_MODE 0x80
    
    #define LIS3DH_STATUS_REG_ZYX_DA_1 0x08
    
    
    
    // Brief Address of the ADC output LSB register
    #define LIS3DH_OUT_ADC_3L 0x0C

    // Brief Address of the ADC output MSB register  
    #define LIS3DH_OUT_ADC_3H 0x0D
    
    //Output Registers:
    #define LIS3DH_OUT_X_L 0x28
    #define LIS3DH_OUT_X_H 0x29
    
    #define LIS3DH_OUT_Y_L 0x2A
    #define LIS3DH_OUT_Y_H 0x2B
    
    #define LIS3DH_OUT_Z_L 0x2C
    #define LIS3DH_OUT_Z_H 0x2D
    
#endif
