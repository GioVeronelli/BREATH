/*******************************************************************************
* File Name: PWM_BUZZ_PM.c
* Version 3.30
*
* Description:
*  This file provides the power management source code to API for the
*  PWM.
*
* Note:
*
********************************************************************************
* Copyright 2008-2014, Cypress Semiconductor Corporation.  All rights reserved.
* You may use this file only in accordance with the license, terms, conditions,
* disclaimers, and limitations in the end user license agreement accompanying
* the software package with which this file was provided.
*******************************************************************************/

#include "PWM_BUZZ.h"

static PWM_BUZZ_backupStruct PWM_BUZZ_backup;


/*******************************************************************************
* Function Name: PWM_BUZZ_SaveConfig
********************************************************************************
*
* Summary:
*  Saves the current user configuration of the component.
*
* Parameters:
*  None
*
* Return:
*  None
*
* Global variables:
*  PWM_BUZZ_backup:  Variables of this global structure are modified to
*  store the values of non retention configuration registers when Sleep() API is
*  called.
*
*******************************************************************************/
void PWM_BUZZ_SaveConfig(void) 
{

    #if(!PWM_BUZZ_UsingFixedFunction)
        #if(!PWM_BUZZ_PWMModeIsCenterAligned)
            PWM_BUZZ_backup.PWMPeriod = PWM_BUZZ_ReadPeriod();
        #endif /* (!PWM_BUZZ_PWMModeIsCenterAligned) */
        PWM_BUZZ_backup.PWMUdb = PWM_BUZZ_ReadCounter();
        #if (PWM_BUZZ_UseStatus)
            PWM_BUZZ_backup.InterruptMaskValue = PWM_BUZZ_STATUS_MASK;
        #endif /* (PWM_BUZZ_UseStatus) */

        #if(PWM_BUZZ_DeadBandMode == PWM_BUZZ__B_PWM__DBM_256_CLOCKS || \
            PWM_BUZZ_DeadBandMode == PWM_BUZZ__B_PWM__DBM_2_4_CLOCKS)
            PWM_BUZZ_backup.PWMdeadBandValue = PWM_BUZZ_ReadDeadTime();
        #endif /*  deadband count is either 2-4 clocks or 256 clocks */

        #if(PWM_BUZZ_KillModeMinTime)
             PWM_BUZZ_backup.PWMKillCounterPeriod = PWM_BUZZ_ReadKillTime();
        #endif /* (PWM_BUZZ_KillModeMinTime) */

        #if(PWM_BUZZ_UseControl)
            PWM_BUZZ_backup.PWMControlRegister = PWM_BUZZ_ReadControlRegister();
        #endif /* (PWM_BUZZ_UseControl) */
    #endif  /* (!PWM_BUZZ_UsingFixedFunction) */
}


/*******************************************************************************
* Function Name: PWM_BUZZ_RestoreConfig
********************************************************************************
*
* Summary:
*  Restores the current user configuration of the component.
*
* Parameters:
*  None
*
* Return:
*  None
*
* Global variables:
*  PWM_BUZZ_backup:  Variables of this global structure are used to
*  restore the values of non retention registers on wakeup from sleep mode.
*
*******************************************************************************/
void PWM_BUZZ_RestoreConfig(void) 
{
        #if(!PWM_BUZZ_UsingFixedFunction)
            #if(!PWM_BUZZ_PWMModeIsCenterAligned)
                PWM_BUZZ_WritePeriod(PWM_BUZZ_backup.PWMPeriod);
            #endif /* (!PWM_BUZZ_PWMModeIsCenterAligned) */

            PWM_BUZZ_WriteCounter(PWM_BUZZ_backup.PWMUdb);

            #if (PWM_BUZZ_UseStatus)
                PWM_BUZZ_STATUS_MASK = PWM_BUZZ_backup.InterruptMaskValue;
            #endif /* (PWM_BUZZ_UseStatus) */

            #if(PWM_BUZZ_DeadBandMode == PWM_BUZZ__B_PWM__DBM_256_CLOCKS || \
                PWM_BUZZ_DeadBandMode == PWM_BUZZ__B_PWM__DBM_2_4_CLOCKS)
                PWM_BUZZ_WriteDeadTime(PWM_BUZZ_backup.PWMdeadBandValue);
            #endif /* deadband count is either 2-4 clocks or 256 clocks */

            #if(PWM_BUZZ_KillModeMinTime)
                PWM_BUZZ_WriteKillTime(PWM_BUZZ_backup.PWMKillCounterPeriod);
            #endif /* (PWM_BUZZ_KillModeMinTime) */

            #if(PWM_BUZZ_UseControl)
                PWM_BUZZ_WriteControlRegister(PWM_BUZZ_backup.PWMControlRegister);
            #endif /* (PWM_BUZZ_UseControl) */
        #endif  /* (!PWM_BUZZ_UsingFixedFunction) */
    }


/*******************************************************************************
* Function Name: PWM_BUZZ_Sleep
********************************************************************************
*
* Summary:
*  Disables block's operation and saves the user configuration. Should be called
*  just prior to entering sleep.
*
* Parameters:
*  None
*
* Return:
*  None
*
* Global variables:
*  PWM_BUZZ_backup.PWMEnableState:  Is modified depending on the enable
*  state of the block before entering sleep mode.
*
*******************************************************************************/
void PWM_BUZZ_Sleep(void) 
{
    #if(PWM_BUZZ_UseControl)
        if(PWM_BUZZ_CTRL_ENABLE == (PWM_BUZZ_CONTROL & PWM_BUZZ_CTRL_ENABLE))
        {
            /*Component is enabled */
            PWM_BUZZ_backup.PWMEnableState = 1u;
        }
        else
        {
            /* Component is disabled */
            PWM_BUZZ_backup.PWMEnableState = 0u;
        }
    #endif /* (PWM_BUZZ_UseControl) */

    /* Stop component */
    PWM_BUZZ_Stop();

    /* Save registers configuration */
    PWM_BUZZ_SaveConfig();
}


/*******************************************************************************
* Function Name: PWM_BUZZ_Wakeup
********************************************************************************
*
* Summary:
*  Restores and enables the user configuration. Should be called just after
*  awaking from sleep.
*
* Parameters:
*  None
*
* Return:
*  None
*
* Global variables:
*  PWM_BUZZ_backup.pwmEnable:  Is used to restore the enable state of
*  block on wakeup from sleep mode.
*
*******************************************************************************/
void PWM_BUZZ_Wakeup(void) 
{
     /* Restore registers values */
    PWM_BUZZ_RestoreConfig();

    if(PWM_BUZZ_backup.PWMEnableState != 0u)
    {
        /* Enable component's operation */
        PWM_BUZZ_Enable();
    } /* Do nothing if component's block was disabled before */

}


/* [] END OF FILE */
