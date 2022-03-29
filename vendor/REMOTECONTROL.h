/*
 *    EKSPLA REMOTECONTROL.DLL
 *
 */
/*
 * REMOTECONTROL.H revision history
 *
 *   - DLL version v1.6.0.0 and above:
 *          Added Register type functions
 *          Added rcSetRegFromDoubleA and rcSetRegFromStringA
 */

#ifndef __REMOTECONTROL_H
#define __REMOTECONTROL_H

#include "windows.h"

#ifdef __cplusplus
extern "C" {
#endif


/*
 *   Function return codes
 */

#define RMTCTRLERR_OK                0  // Success, no error
#define RMTCTRLERR_NOMOREDATA        1  // End of registers list or enumerated values list
#define RMTCTRLERR_NOCFGFILE         2  // No config file found
#define RMTCTRLERR_WRONGCFGFILE      3  // wrong CFG file
#define RMTCTRLERR_BUFFERTOOSHORT    4  // application provided return buffer is too short
#define RMTCTRLERR_NOSUCHDEVICE      5  // no such device name
#define RMTCTRLERR_NOSUCHREGISTER    6  // no such register name
#define RMTCTRLERR_CANTCONNECT       7
#define RMTCTRLERR_TIMEOUT           8  // timeout waiting for device answer
#define RMTCTRLERR_READONLY          9  // register is read only
#define RMTCTRLERR_NOT_NV           10  // register is not NV
#define RMTCTRLERR_HILIMIT          11  // attempt to set value above upper limit
#define RMTCTRLERR_LOLIMIT          12  // attempt to set value below bottom limit
#define RMTCTRLERR_NOSUCHVALUE      13  // attempt to set not allowed value
#define RMTCTRLERR_NOTLOGGED        14  // register is not being logged
#define RMTCTRLERR_MEMORYFULL       15  // not enough memory
#define RMTCTRLERR_LOGISEMPTY       16  // no data in the queue yet
#define RMTCTRLERR_ALREADYCONNECTED 17  // already connected, please disconnect first
#define RMTCTRLERR_NOTYETCONNECTED  18  // not connected, please connect first


/*
  Function rcGetRegFromLogAsDouble and rcGetRegFromLogAsString
  may or return value with RMTCTRLERR_LOGOVERFLOW.
  This happens when data retrieval succeeds, but Log FIFO
  overflow is detected.
*/
#define RMTCTRLERR_LOGOVERFLOW  0x80000000 // Log FIFO overrun occured


/*
 *   Functions list

 Connection functions:
   rcConnect
   rcDisconnect

 Devices and registers enumeration functions:
   rcGetFirstDeviceName
   rcGetNextDeviceName
   rcGetFirstRegisterName
   rcGetNextRegisterName

 Register classification functions
   rcIsRegisterWriteable
   rcIsRegisterNV
   rcGetRegFirstEnumValue
   rcGetRegNextEnumValue

 Register access functions:
   rcGetRegAsDouble
   rcSetRegFromDouble
   rcSetRegFromDoubleA
   rcSetRegNVFromDouble
   rcGetRegAsString
   rcSetRegFromString
   rcSetRegFromStringA
   rcSetRegNVFromString

 Register log and access functions:
   rcLogRegStart
   rcLogRegStop
   rcGetRegFromLogAsDouble
   rcGetRegFromLogAsString
 *
 */



/***************************************************************
    Function:     Connect

    Description:  Makes a connection attempt

    Arguments:    connectiontype: 0 - direct
                                  1 - rs232
                  comportnumber:  1 - COM1
                                  2 - COM2
                                  ...

    Return value: error code, one of RMTCTRLERR_xxx list
 */
int __stdcall rcConnect(int connectiontype, int comportnumber);





/***************************************************************
    Function:     Disconnect

    Description:  Disconnects

    Arguments:    none

    Return value: error code, one of RMTCTRLERR_xxx list
 */
int __stdcall rcDisconnect(void);




/***************************************************************
    Function:     GetFirstDeviceName

    Description:  Get the name of first device in the list. Use
                  GetNextDeviceName() in a loop to retrieve all
                  device names.

    Arguments:    devname:       pointer to C string. GetFirstDeviceName will
                                 write to *devname
                  maxdevnamelen: Maximum length of devname string including
                                 terminatiion character.

    Return value: error code, one of RMTCTRLERR_xxx list
 */
int __stdcall rcGetFirstDeviceName(char *devname, int maxdevnamelen);



/***************************************************************
    Function:     GetNextDeviceName

    Description:  Get the name of next device in the list. Use
                  GetFirstDeviceName() to restart retrieval from
                  the beginning of device names list

    Arguments:    devname:       pointer to C string. GetFirstDeviceName will
                                 write to *devname
                  maxdevnamelen: Maximum length of devname string including
                                 terminatiion character.

    Return value: error code, one of RMTCTRLERR_xxx list
                  On the end of devices list, GetNextDeviceName will
                  return RMTCTRLERR_NOMOREDATA
 */
int __stdcall rcGetNextDeviceName(char *devname, int maxdevnamelen);



/***************************************************************
    Function:     GetFirstRegisterName

    Description:  Get first register name of specific device. Use
                  GetNextRegName() in a loop to retrieve all device
                  register names.

    Arguments:    devname:       pointer to device name string.

                  regname:       pointer to register name string. GetFirstRegisterName will
                                 write to *regname
                  maxregnamelen: Maximum length of string including terminatiion
                                 character.

    Return value: error code, one of RMTCTRLERR_xxx list
 */
int __stdcall rcGetFirstRegisterName(const char * devname, char *regname, int maxregnamelen);



/***************************************************************
    Function:     GetNextRegisterName

    Description:  Get next register name of specific device. Use GetFirstRegisterName()
                  to reset retrival of register names from the beginning.

    Arguments:    regname:       pointer to C string. GetNextParName will
                                 write to *parname

                  maxregnamelen: Maximum length of string including terminatiion
                                 character.

    Return value: error code, one of RMTCTRLERR_xxx list.
                  On the end of registers list, GetNextRegName will
                  return RMTCTRLERR_NOMOREDATA
 */
int __stdcall rcGetNextRegisterName(char *regname, int maxparlen);



/***************************************************************
    Function:     rcIsRegisterWriteable

    Description:  Determine if register is writeable

    Arguments:    devname:     pointer to device name string

                  regname:     pointer to register name string.

                  isWriteable: pointer to integer. On success
                               rcIsRegisterWriteable will write:
                                1 - in case register is writeable
                                0 - in case register is not writeable

    Return value: error code, one of RMTCTRLERR_xxx list.
 */
int __stdcall rcIsRegisterWriteable(const char *devname, const char *regname,
                              int *isWriteable);



/***************************************************************
    Function:     rcIsRegisterNV

    Description:  Determine if register is NV (nonvolatile)

    Arguments:    devname:     pointer to device name string

                  regname:     pointer to register name string.

                  isNV:        pointer to integer. On success
                               rcIsRegisterNV will write:
                                1 - in case register is NV
                                0 - in case register is not NV

    Return value: error code, one of RMTCTRLERR_xxx list.
 */
int __stdcall rcIsRegisterNV(const char *devname, const char *regname,
                              int *isNV);



/***************************************************************
    Function:     rcGetRegFirstEnumValue

    Description:  For registers having list of values, like ON, OFF, DISABLE etc,
                  this function returns first available value.
                  Attempt to get enumerated value of numeric register
                  returns RMTCTRLERR_NOMOREDATA.
                  Use rcGetRegNextEnumValue() in a loop to
                  retrieve all available enumerated register values.

    Arguments:    devname:        pointer to device name string.

                  regname:        pointer to register name string.

                  enumname:       pointer to value. rcGetRegFirstEnumValue will
                                  write value string to *enumname

                  maxenumnamelen: Maximum length of enumname string including terminatiion
                                  character.

    Return value: error code, one of RMTCTRLERR_xxx list
 */
int __stdcall rcGetRegFirstEnumValue(const char * devname, const char *regname,
                                           char * enumname, int maxenumnamelen);



/***************************************************************
    Function:     rcGetRegNextEnumValue

    Description:  See rcGetRegFirstEnumValue.
                  rcGetRegNextEnumValue() will return next available listed
                  value.

    Arguments:    devname:        pointer to device name string.

                  regname:        pointer to register name string.

                  enumname:       pointer to value. rcGetRegNextEnumValue will
                                  write value string to *enumname

                  maxenumnamelen: Maximum length of enumname string including terminatiion
                                  character.

    Return value: error code, one of RMTCTRLERR_xxx list
 */
int __stdcall rcGetRegNextEnumValue(const char * devname, const char *regname,
                                          char * enumname, int maxenumnamelen);



/***************************************************************
    Function:     GetRegAsDouble

    Description:  Return register value as double.

    Arguments:    devname:   pointer to device name string

                  regname:   pointer to register name string.

                  value:     pointer to double, rcGetRegAsDouble will overwrite
                             on success

                  timeout:   timeout in milliseconds. (-1) - infinite timeout

                  timestamp: pointer to int. In case timestamp is not a NULL,
                             rcGetRegAsDouble will write to *timestamp the time
                             stamp of received message

    Return value: error code, one of RMTCTRLERR_xxx list.
 */
int __stdcall rcGetRegAsDouble(const char *devname, const char *regname,
                              double *value,       int timeout,
                              int *timestamp);



/***************************************************************
    Function:     SetRegFromDouble

    Description:  Set register value from double variable.

    Arguments:    devname:   pointer to device name string

                  regname:   pointer to register name string.

                  value:     value

    Return value: error code, one of RMTCTRLERR_xxx list.
 */
int __stdcall rcSetRegFromDouble(const char *devname, const char *regname, double value);



/***************************************************************
    Function:     SetRegFromDoubleA

    Description:  Set register value from double variable.

    Arguments:    devname:     pointer to device name string

                  regname:     pointer to register name string.

                  value:       value

                  forcelimits: forcelimits==0 - complain when value is out of limits
                               forcelimits!=0 - force value limits

    Return value: error code, one of RMTCTRLERR_xxx list.
 */
int __stdcall rcSetRegFromDoubleA(const char *devname, const char *regname, double value,
                                  int forcelimits);




/***************************************************************
    Function:     SetRegNVFromDouble

    Description:  Set register NV value from double variable.

    Arguments:    devname:   pointer to device name string

                  regname:   pointer to register name string.

                  value:     value

    Return value: error code, one of RMTCTRLERR_xxx list.
 */
int __stdcall rcSetRegNVFromDouble(const char *devname, const char *regname, double value);



/***************************************************************
    Function:     GetRegAsString

    Description:  Return register value as string.

    Arguments:    devname:   pointer to device name string

                  regname:   pointer to register name string.

                  value:     pointer to string, GetRegAsString will overwrite

                  maxvallen: maximum length of value string, including terminating character

                  timeout:   timeout in milliseconds. (-1) - infinite timeout

                  timestamp: pointer to int. In case timestamp is not a NULL,
                             rcGetRegAsDouble will write to *timestamp the time
                             stamp of received message

    Return value: error code, one of RMTCTRLERR_xxx list.
 */
int __stdcall rcGetRegAsString(const char *devname, const char *regname,
                              char *value, int maxvallen, int timeout,
                              int *timestamp);



/***************************************************************
    Function:     SetRegFromString

    Description:  Set register value from string.

    Arguments:    devname:   pointer to device name string

                  regname:   pointer to register name string.

                  value:     pointer to string

    Return value: error code, one of RMTCTRLERR_xxx list.
 */
int __stdcall rcSetRegFromString(const char *devname, const char *regname, const char *value);



/***************************************************************
    Function:     SetRegFromStringA

    Description:  Set register value from string.

    Arguments:    devname:     pointer to device name string

                  regname:     pointer to register name string.

                  value:       pointer to string

                  forcelimits: forcelimits==0 - complain when value is out of limits
                               forcelimits!=0 - force value limits

    Return value: error code, one of RMTCTRLERR_xxx list.
 */
int __stdcall rcSetRegFromStringA(const char *devname, const char *regname, const char *value,
                                  int forcelimits);


/***************************************************************
    Function:     SetRegNVFromString

    Description:  Set register value from string.

    Arguments:    devname:   pointer to device name string

                  regname:   pointer to register name string.

                  value:     pointer to string

    Return value: error code, one of RMTCTRLERR_xxx list.
 */
int __stdcall rcSetRegNVFromString(const char *devname, const char *regname, const char *value);



/***************************************************************
    Function:     rcLogRegStart

    Description:  Start logging register

    Arguments:    devname:   pointer to device name string

                  regname:   pointer to register name string.

                  queuesize: Size of memory to allocate
                             for data queue.

    Return value: error code, one of RMTCTRLERR_xxx list.
 */
int __stdcall rcLogRegStart(const char *devname, const char *regname,
                          int queuesize);



/***************************************************************
    Function:     rcLogRegStop

    Description:  Stop logging register

    Arguments:    devname:   pointer to device name string

                  regname:   pointer to register name string.

    Return value: error code, one of RMTCTRLERR_xxx list.
 */
int __stdcall rcLogRegStop(const char *devname, const char *regname);



/***************************************************************
    Function:     rcGetRegFromLogAsDouble

    Description:  Get register value from log queue as double value.

    Arguments:    devname:   pointer to device name string

                  regname:   pointer to register name string.

                  value:     pointer to double, rcGetRegAsDouble will overwrite

                  timestamp: pointer to int. In case timestamp is not a NULL,
                             rcGetRegAsDouble will write to *timestamp the time
                             stamp of received message

    Return value: error code, one of RMTCTRLERR_xxx list.
 */
int __stdcall rcGetRegFromLogAsDouble(const char *devname, const char *regname,
                              double *value,  int *timestamp);



/***************************************************************
    Function:     rcGetRegFromLogAsString

    Description:  Get register value from log queue as string.

    Arguments:    devname:   pointer to device name string

                  regname:   pointer to register name string.

                  value:     pointer to string, GetRegAsString will overwrite

                  maxvallen: maximum length of value string, including terminating character

                  timestamp: pointer to int. In case timestamp is not a NULL,
                             rcGetRegAsDouble will write to *timestamp the time
                             stamp of received message

    Return value: error code, one of RMTCTRLERR_xxx list.
 */
int __stdcall rcGetRegFromLogAsString(const char *devname, const char *regname,
                              char *value, int maxvallen, int *timestamp);





#ifdef __cplusplus
} // extern "C"
#endif


#endif //__REMOTECONTROL_H
