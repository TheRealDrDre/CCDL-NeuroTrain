# ------------------------------------------------------------------ #
# EMOTIV SUITE VARIABLES
# ------------------------------------------------------------------ #

ED_COUNTER = 0
ED_INTERPOLATED = 1
ED_RAW_CQ = 2

ED_CMS = 0
ED_DRL = 1

ED_AF3 = 3
ED_F7 = 4 
ED_F3 = 5
ED_FC5 = 6
ED_T7 = 7
ED_P7 = 8
ED_O1 = 9
ED_O2 = 10
ED_P8 = 11
ED_T8 = 12
ED_FC6 = 13
ED_F4 = 14
ED_F8 = 15
ED_AF4 = 16
ED_GYROX = 17
ED_GYROY = 18
ED_TIMESTAMP = 19
ED_ES_TIMESTAMP = 20
ED_FUNC_ID = 21
ED_FUNC_VALUE = 22
ED_MARKER = 23
ED_SYNC_SIGNAL = 24

## Quick list of sensors

SENSORS = (ED_AF3, ED_F7, ED_F3, ED_FC5, ED_T7, ED_P7, ED_O1, ED_O2,
           ED_P8, ED_T8, ED_FC6, ED_F4, ED_F8, ED_AF4)

COMPLETE_SENSORS = (ED_CMS, ED_DRL, ED_AF3, ED_F7, ED_F3, ED_FC5, ED_T7, ED_P7, 
                    ED_O1, ED_O2, ED_P8, ED_T8, ED_FC6, ED_F4, ED_F8, ED_AF4)


SENSOR_NAMES = {ED_CMS : "CMS", ED_DRL : "DRL",  # The two Common Sense Mode references
                ED_AF3 : "AF3", ED_F7 : "F7", ED_F3 : "F3", ED_FC5 : "FC5",
                ED_T7 : "T7", ED_P7 : "P7", ED_O1 : "O1", ED_O2 : "O2",
                ED_P8 : "P8", ED_T8 : "T8", ED_FC6 : "FC6", ED_F4 : "F4",
                ED_F8 : "F8", ED_AF4 : "AF4"}


CHANNELS = (ED_COUNTER, ED_AF3, ED_F7, ED_F3, ED_FC5, ED_T7, ED_P7,
            ED_O1, ED_O2, ED_P8, ED_T8, ED_FC6, ED_F4, ED_F8, ED_AF4,
            ED_GYROX, ED_GYROY, ED_TIMESTAMP, ED_FUNC_ID, ED_FUNC_VALUE,
            ED_MARKER, ED_SYNC_SIGNAL)

CHANNEL_NAMES = {ED_COUNTER : "Counter",
                 # EEG Channels proper
                 ED_AF3 : "AF3", ED_F7 : "F7", ED_F3 : "F3", ED_FC5 : "FC5",
                 ED_T7 : "T7", ED_P7 : "P7", ED_O1 : "O1", ED_O2 : "O2",
                 ED_P8 : "P8", ED_T8 : "T8", ED_FC6 : "FC6", ED_F4 : "F4",
                 ED_F8 : "F8", ED_AF4 : "AF4",
                 # Extra
                 ED_GYROX : "GyroX", ED_GYROY : "GyroY",
                 ED_TIMESTAMP : "Timestamp", ED_FUNC_ID : "FUNC_ID",
                 ED_FUNC_VALUE : "FUNC_VALUE", ED_MARKER : "MARKER",
                 ED_SYNC_SIGNAL : "SYNC_SIGNAL"}

## Wireless signal

EDK_NO_SIGNAL = 0
EDK_BAD_SIGNAL = 1
EDK_GOOD_SIGNAL = 2

## Hardware events

EE_User_Added = 0x0010 
EE_User_Removed = 0x0020
EE_EmoState_Updated = 0x0040
EE_Profile_Event = 0x0080 
EE_Cognitiv_Event = 0x0100
EE_Expressiv_Event = 0x0200 
EE_Internal_State_Changed = 0x0400 
EE_Emulator_Error = 0x0001
EDK_NO_EVENT = 0x0600

## Error codes

EDK_OK = 0x0000 
EDK_UNKNOWN_ERROR = 0x0001  
EDK_INVALID_PROFILE_ARCHIVE = 0x0101  
EDK_NO_USER_FOR_BASE_PROFILE = 0x0102 
EDK_CANNOT_ACQUIRE_DATA = 0x0200 
EDK_BUFFER_TOO_SMALL = 0x0300 
EDK_OUT_OF_RANGE = 0x0301  
EDK_INVALID_PARAMETER = 0x0302 
EDK_PARAMETER_LOCKED = 0x0303