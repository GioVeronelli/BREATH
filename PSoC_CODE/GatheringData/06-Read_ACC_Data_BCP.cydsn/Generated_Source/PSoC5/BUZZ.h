/*******************************************************************************
* File Name: BUZZ.h  
* Version 2.20
*
* Description:
*  This file contains Pin function prototypes and register defines
*
* Note:
*
********************************************************************************
* Copyright 2008-2015, Cypress Semiconductor Corporation.  All rights reserved.
* You may use this file only in accordance with the license, terms, conditions, 
* disclaimers, and limitations in the end user license agreement accompanying 
* the software package with which this file was provided.
*******************************************************************************/

#if !defined(CY_PINS_BUZZ_H) /* Pins BUZZ_H */
#define CY_PINS_BUZZ_H

#include "cytypes.h"
#include "cyfitter.h"
#include "cypins.h"
#include "BUZZ_aliases.h"

/* APIs are not generated for P15[7:6] */
#if !(CY_PSOC5A &&\
	 BUZZ__PORT == 15 && ((BUZZ__MASK & 0xC0) != 0))


/***************************************
*        Function Prototypes             
***************************************/    

/**
* \addtogroup group_general
* @{
*/
void    BUZZ_Write(uint8 value);
void    BUZZ_SetDriveMode(uint8 mode);
uint8   BUZZ_ReadDataReg(void);
uint8   BUZZ_Read(void);
void    BUZZ_SetInterruptMode(uint16 position, uint16 mode);
uint8   BUZZ_ClearInterrupt(void);
/** @} general */

/***************************************
*           API Constants        
***************************************/
/**
* \addtogroup group_constants
* @{
*/
    /** \addtogroup driveMode Drive mode constants
     * \brief Constants to be passed as "mode" parameter in the BUZZ_SetDriveMode() function.
     *  @{
     */
        #define BUZZ_DM_ALG_HIZ         PIN_DM_ALG_HIZ
        #define BUZZ_DM_DIG_HIZ         PIN_DM_DIG_HIZ
        #define BUZZ_DM_RES_UP          PIN_DM_RES_UP
        #define BUZZ_DM_RES_DWN         PIN_DM_RES_DWN
        #define BUZZ_DM_OD_LO           PIN_DM_OD_LO
        #define BUZZ_DM_OD_HI           PIN_DM_OD_HI
        #define BUZZ_DM_STRONG          PIN_DM_STRONG
        #define BUZZ_DM_RES_UPDWN       PIN_DM_RES_UPDWN
    /** @} driveMode */
/** @} group_constants */
    
/* Digital Port Constants */
#define BUZZ_MASK               BUZZ__MASK
#define BUZZ_SHIFT              BUZZ__SHIFT
#define BUZZ_WIDTH              1u

/* Interrupt constants */
#if defined(BUZZ__INTSTAT)
/**
* \addtogroup group_constants
* @{
*/
    /** \addtogroup intrMode Interrupt constants
     * \brief Constants to be passed as "mode" parameter in BUZZ_SetInterruptMode() function.
     *  @{
     */
        #define BUZZ_INTR_NONE      (uint16)(0x0000u)
        #define BUZZ_INTR_RISING    (uint16)(0x0001u)
        #define BUZZ_INTR_FALLING   (uint16)(0x0002u)
        #define BUZZ_INTR_BOTH      (uint16)(0x0003u) 
    /** @} intrMode */
/** @} group_constants */

    #define BUZZ_INTR_MASK      (0x01u) 
#endif /* (BUZZ__INTSTAT) */


/***************************************
*             Registers        
***************************************/

/* Main Port Registers */
/* Pin State */
#define BUZZ_PS                     (* (reg8 *) BUZZ__PS)
/* Data Register */
#define BUZZ_DR                     (* (reg8 *) BUZZ__DR)
/* Port Number */
#define BUZZ_PRT_NUM                (* (reg8 *) BUZZ__PRT) 
/* Connect to Analog Globals */                                                  
#define BUZZ_AG                     (* (reg8 *) BUZZ__AG)                       
/* Analog MUX bux enable */
#define BUZZ_AMUX                   (* (reg8 *) BUZZ__AMUX) 
/* Bidirectional Enable */                                                        
#define BUZZ_BIE                    (* (reg8 *) BUZZ__BIE)
/* Bit-mask for Aliased Register Access */
#define BUZZ_BIT_MASK               (* (reg8 *) BUZZ__BIT_MASK)
/* Bypass Enable */
#define BUZZ_BYP                    (* (reg8 *) BUZZ__BYP)
/* Port wide control signals */                                                   
#define BUZZ_CTL                    (* (reg8 *) BUZZ__CTL)
/* Drive Modes */
#define BUZZ_DM0                    (* (reg8 *) BUZZ__DM0) 
#define BUZZ_DM1                    (* (reg8 *) BUZZ__DM1)
#define BUZZ_DM2                    (* (reg8 *) BUZZ__DM2) 
/* Input Buffer Disable Override */
#define BUZZ_INP_DIS                (* (reg8 *) BUZZ__INP_DIS)
/* LCD Common or Segment Drive */
#define BUZZ_LCD_COM_SEG            (* (reg8 *) BUZZ__LCD_COM_SEG)
/* Enable Segment LCD */
#define BUZZ_LCD_EN                 (* (reg8 *) BUZZ__LCD_EN)
/* Slew Rate Control */
#define BUZZ_SLW                    (* (reg8 *) BUZZ__SLW)

/* DSI Port Registers */
/* Global DSI Select Register */
#define BUZZ_PRTDSI__CAPS_SEL       (* (reg8 *) BUZZ__PRTDSI__CAPS_SEL) 
/* Double Sync Enable */
#define BUZZ_PRTDSI__DBL_SYNC_IN    (* (reg8 *) BUZZ__PRTDSI__DBL_SYNC_IN) 
/* Output Enable Select Drive Strength */
#define BUZZ_PRTDSI__OE_SEL0        (* (reg8 *) BUZZ__PRTDSI__OE_SEL0) 
#define BUZZ_PRTDSI__OE_SEL1        (* (reg8 *) BUZZ__PRTDSI__OE_SEL1) 
/* Port Pin Output Select Registers */
#define BUZZ_PRTDSI__OUT_SEL0       (* (reg8 *) BUZZ__PRTDSI__OUT_SEL0) 
#define BUZZ_PRTDSI__OUT_SEL1       (* (reg8 *) BUZZ__PRTDSI__OUT_SEL1) 
/* Sync Output Enable Registers */
#define BUZZ_PRTDSI__SYNC_OUT       (* (reg8 *) BUZZ__PRTDSI__SYNC_OUT) 

/* SIO registers */
#if defined(BUZZ__SIO_CFG)
    #define BUZZ_SIO_HYST_EN        (* (reg8 *) BUZZ__SIO_HYST_EN)
    #define BUZZ_SIO_REG_HIFREQ     (* (reg8 *) BUZZ__SIO_REG_HIFREQ)
    #define BUZZ_SIO_CFG            (* (reg8 *) BUZZ__SIO_CFG)
    #define BUZZ_SIO_DIFF           (* (reg8 *) BUZZ__SIO_DIFF)
#endif /* (BUZZ__SIO_CFG) */

/* Interrupt Registers */
#if defined(BUZZ__INTSTAT)
    #define BUZZ_INTSTAT            (* (reg8 *) BUZZ__INTSTAT)
    #define BUZZ_SNAP               (* (reg8 *) BUZZ__SNAP)
    
	#define BUZZ_0_INTTYPE_REG 		(* (reg8 *) BUZZ__0__INTTYPE)
#endif /* (BUZZ__INTSTAT) */

#endif /* CY_PSOC5A... */

#endif /*  CY_PINS_BUZZ_H */


/* [] END OF FILE */
