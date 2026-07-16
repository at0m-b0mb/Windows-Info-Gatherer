@ECHO OFF
TITLE Windows OS Info by HackProKP - Enhanced Version
ECHO --------------------------------------
ECHO  Windows Operating System Information
ECHO --------------------------------------
ECHO.

REM Retrieve basic system information
ECHO System Information:
systeminfo | findstr /C:"Host Name" /C:"Domain" /C:"OS Name" /C:"OS Version" /C:"Registered Owner" /C:"Registered Organization" /C:"System Manufacturer" /C:"System Model" /C:"System Type"
ECHO.

REM Retrieve CPU details
ECHO Processor Information:
wmic cpu get Name, NumberOfCores, MaxClockSpeed
ECHO.

REM Retrieve memory details
ECHO Memory Information:
wmic memorychip get Capacity
ECHO.

REM Retrieve network information
ECHO Network Configuration:
ipconfig | findstr /C:"IPv4 Address" /C:"Subnet Mask" /C:"Default Gateway"
getmac
ECHO.

REM Retrieve current user information
ECHO Logged-in User:
whoami
ECHO.

PAUSE
