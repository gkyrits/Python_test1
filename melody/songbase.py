from tone import *

#----------------------------------------------------------------------------------------
__melody_1 = (
  NOTE_G4, NOTE_AS4, NOTE_C5, NOTE_D5, NOTE_D5, NOTE_C5, NOTE_DS5, NOTE_D5,
  NOTE_D5, NOTE_C5, NOTE_C5, NOTE_AS4, NOTE_A4, NOTE_AS4, NOTE_AS4,
  NOTE_AS4, NOTE_C5, NOTE_D5,
  
  NOTE_D5, NOTE_D5, NOTE_DS5, NOTE_D5, NOTE_DS5,
  NOTE_DS5, NOTE_DS5, NOTE_C5, NOTE_DS5, NOTE_C5, NOTE_C5, NOTE_D5, NOTE_C5, NOTE_D5, NOTE_D5, NOTE_AS4, NOTE_D5,
  NOTE_AS4, NOTE_AS4, NOTE_A4, NOTE_AS4, NOTE_A4, NOTE_A4, NOTE_AS4, NOTE_A4, NOTE_AS4, NOTE_AS4, NOTE_G4, NOTE_AS4,
  NOTE_G4, NOTE_G4, NOTE_F4, NOTE_G4, NOTE_F4, NOTE_F4,

  NOTE_C5,
  NOTE_C5, NOTE_C5, NOTE_C5, NOTE_C5, NOTE_C5, NOTE_C5, NOTE_D5, NOTE_C5, NOTE_D5, NOTE_D5,
  NOTE_F5, NOTE_D5, NOTE_F5, NOTE_F5, NOTE_D5, NOTE_F5, NOTE_D5, NOTE_D5, NOTE_C5, NOTE_D5,
  NOTE_C5, NOTE_C5, NOTE_AS4, NOTE_C5, NOTE_AS4, NOTE_AS4, NOTE_D5, NOTE_C5, NOTE_D5, NOTE_D5,


  NOTE_DS5,
  NOTE_DS5, NOTE_DS5, NOTE_C5, NOTE_DS5, NOTE_C5, NOTE_C5, NOTE_D5, NOTE_C5, NOTE_D5, NOTE_D5,
  NOTE_AS4, NOTE_D5, NOTE_AS4, NOTE_AS4, NOTE_A4, NOTE_AS4, NOTE_A4, NOTE_A4, NOTE_AS4, NOTE_A4,
  NOTE_AS4, NOTE_AS4, NOTE_G4, NOTE_AS4, NOTE_G4, NOTE_G4, NOTE_F4, NOTE_G4, NOTE_F4, NOTE_F4,

  REST
)
__durations_1 = (
  4, 3, 4, 4, 2, 3, 4, 1,
  3, 4, 2, 4, 3, 4, 1,
  3, 4, 1,

  4, 3, 4, 4, 4,
  8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8,
  8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8,
  8, 8, 8, 8, 8, 8,

  4,
  8, 8, 8, 8, 8, 8, 8, 8, 8, 8,
  8, 8, 8, 8, 8, 8, 8, 8, 8, 8,
  8, 8, 8, 8, 8, 8, 8, 8, 8, 8,

  4,
  8, 8, 8, 8, 8, 8, 8, 8, 8, 8,
  8, 8, 8, 8, 8, 8, 8, 8, 8, 8,
  8, 8, 8, 8, 8, 8, 8, 8, 8, 8,

  1
)
melody_1 = ( __melody_1, __durations_1, "Kerosene" )

#----------------------------------------------------------------------------------------
__melody_2 = (
  NOTE_C4, NOTE_D4, NOTE_E4, NOTE_F4,
  NOTE_E4, NOTE_C4, NOTE_C4, NOTE_G4,
  REST,

  NOTE_G4, NOTE_G4, NOTE_F4, NOTE_E4, NOTE_D4,
  NOTE_D4, NOTE_D4, NOTE_E4, NOTE_F4, NOTE_E4,
  NOTE_C4, NOTE_C4, NOTE_D4, NOTE_E4, NOTE_D4, NOTE_C4, NOTE_B3, NOTE_A3, NOTE_G3,

  NOTE_G4, NOTE_G4, NOTE_F4, NOTE_E4, NOTE_D4,
  NOTE_D4, NOTE_D4, NOTE_E4, NOTE_F4, NOTE_E4,
  NOTE_C4, NOTE_D4, NOTE_E4, NOTE_F4, NOTE_E4, NOTE_D4, NOTE_C4, NOTE_B3, NOTE_C4,
  REST,

  NOTE_B3, NOTE_C4, REST,
  NOTE_B3, NOTE_C4, REST,
)
__durations_2 = (
  4, 4, 4, 2,
  4, 2, 2, 4,
  1,

  4, 4, 4, 4, 1,
  4, 4, 4, 4, 1,
  4, 2, 2, 2, 2, 2, 4, 4, 1,

  4, 4, 4, 4, 1,
  4, 4, 4, 4, 1,
  4, 2, 2, 2, 2, 2, 4, 4, 2,
  2,

  2, 1, 4,
  2, 1, 4,
)
melody_2 = ( __melody_2, __durations_2, "Right Here Waiting" )

#----------------------------------------------------------------------------------------
__melody_3 = (
  NOTE_A4, REST, NOTE_B4, REST, NOTE_C5, REST, NOTE_A4, REST,
  NOTE_D5, REST, NOTE_E5, REST, NOTE_D5, REST,

  NOTE_G4, NOTE_A4, NOTE_C5, NOTE_A4, NOTE_E5, NOTE_E5, REST,
  NOTE_D5, REST,

  NOTE_G4, NOTE_A4, NOTE_C5, NOTE_A4, NOTE_D5, NOTE_D5, REST,
  NOTE_C5, REST, NOTE_B4, NOTE_A4, REST,

  NOTE_G4, NOTE_A4, NOTE_C5, NOTE_A4, NOTE_C5, NOTE_D5, REST,
  NOTE_B4, NOTE_A4, NOTE_G4, REST, NOTE_G4, REST, NOTE_D5, REST, NOTE_C5, REST,

  NOTE_G4, NOTE_A4, NOTE_C5, NOTE_A4, NOTE_E5, NOTE_E5, REST,
  NOTE_D5, REST,

  NOTE_G4, NOTE_A4, NOTE_C5, NOTE_A4, NOTE_G5, NOTE_B4, REST,
  NOTE_C5, REST, NOTE_B4, NOTE_A4, REST,

  NOTE_G4, NOTE_A4, NOTE_C5, NOTE_A4, NOTE_C5, NOTE_D5, REST,
  NOTE_B4, NOTE_A4, NOTE_G4, REST, NOTE_G4, REST, NOTE_D5, REST, NOTE_C5, REST,

  NOTE_C5, REST, NOTE_D5, REST, NOTE_G4, REST, NOTE_D5, REST, NOTE_E5, REST,
  NOTE_G5, NOTE_F5, NOTE_E5, REST,

  NOTE_C5, REST, NOTE_D5, REST, NOTE_G4, REST
)
__durations_3 = (
  8, 8, 8, 8, 8, 8, 8, 4,
  8, 8, 8, 8, 2, 2,

  8, 8, 8, 8, 2, 8, 8,
  2, 8,

  8, 8, 8, 8, 2, 8, 8,
  4, 8, 8, 8, 8,

  8, 8, 8, 8, 2, 8, 8,
  2, 8, 4, 8, 8, 8, 8, 8, 1, 4,

  8, 8, 8, 8, 2, 8, 8,
  2, 8,

  8, 8, 8, 8, 2, 8, 8,
  2, 8, 8, 8, 8,

  8, 8, 8, 8, 2, 8, 8,
  4, 8, 3, 8, 8, 8, 8, 8, 1, 4,

  2, 6, 2, 6, 4, 4, 2, 6, 2, 3,
  8, 8, 8, 8,

  2, 6, 2, 6, 2, 1
)
melody_3 = ( __melody_3, __durations_3, "Never Gonna Give You Up" )

#----------------------------------------------------------------------------------------
__melody_4 = (
  NOTE_GS4, NOTE_GS4, NOTE_GS4, NOTE_G4, NOTE_F4, NOTE_F4, NOTE_F4, NOTE_F4,
  NOTE_G4, NOTE_G4, NOTE_G4, NOTE_G4, NOTE_G4, NOTE_G4,NOTE_F4,NOTE_F4,
  NOTE_GS4, NOTE_GS4, NOTE_GS4, NOTE_G4, NOTE_F4, NOTE_F4, NOTE_F4, NOTE_F4,
  NOTE_G4, NOTE_G4, NOTE_G4, NOTE_G4, NOTE_G4,

  NOTE_DS5, NOTE_D5, NOTE_DS5, NOTE_C5, REST,
  NOTE_DS5, NOTE_D5, REST,
  NOTE_F5, NOTE_DS5, REST,

  NOTE_DS5, NOTE_D5, NOTE_DS5, NOTE_C5, REST,
  NOTE_DS5, NOTE_D5, REST,
  NOTE_F5, NOTE_DS5, REST,

  NOTE_DS5, NOTE_D5, NOTE_DS5, NOTE_C5, REST,
  NOTE_DS5, NOTE_D5, REST,
  NOTE_F5, NOTE_DS5, REST,

  NOTE_AS4, NOTE_C5, NOTE_AS5, NOTE_GS5, NOTE_G5, NOTE_G5,
)
__durations_4 = (
  4, 4, 4, 4, 4, 4, 4, 4,
  4, 4, 4, 4, 4, 4, 4, 4,
  4, 4, 4, 4, 4, 4, 4, 4,
  4, 4, 4, 4, 4,

  4, 4, 4, 2, 4,
  4, 2, 4,
  4, 2, 2,

  4, 4, 4, 2, 4,
  4, 2, 4,
  4, 2, 2,

  4, 4, 4, 2, 4,
  4, 2, 4,
  4, 2, 2,

  4, 4, 4, 2, 2, 1,
)
melody_4 = ( __melody_4, __durations_4, "Hymn for the weekend" )

#----------------------------------------------------------------------------------------
__melody_5 = (
  NOTE_F4, NOTE_AS5, NOTE_GS4, NOTE_CS4, REST,
  NOTE_AS5, NOTE_AS5, NOTE_CS6, NOTE_AS5, NOTE_AS5, NOTE_GS4, NOTE_F4,
  NOTE_GS4, NOTE_AS5, NOTE_CS6, NOTE_AS5, NOTE_AS5, NOTE_GS4, NOTE_F4, NOTE_GS4,
  NOTE_AS5, NOTE_CS6, NOTE_AS5, NOTE_AS5, NOTE_F5,
  NOTE_DS5, NOTE_CS5, NOTE_AS5, NOTE_AS5, NOTE_AS5,  NOTE_GS4, NOTE_F4, NOTE_GS4,
  NOTE_AS5, NOTE_CS6, NOTE_AS5, NOTE_AS5, NOTE_GS4, NOTE_F4, NOTE_GS4,
  NOTE_AS5, NOTE_CS6, NOTE_AS5, NOTE_AS5, NOTE_GS4, NOTE_F4, NOTE_GS4,
  NOTE_AS5, NOTE_CS6, NOTE_AS5, NOTE_AS5, NOTE_F5,
  NOTE_DS5, NOTE_CS5, NOTE_AS5, NOTE_AS5, NOTE_F5, NOTE_F5, NOTE_F5,
  REST
)
__durations_5 = (
  8, 4, 4, 4, 2,
  4, 4, 4, 2, 4, 4, 4,
  4, 4, 4, 2, 4, 4, 4, 4,
  4, 4, 2, 4, 2,
  8, 8, 4, 2, 4, 4, 4, 4,
  4, 4, 2, 4, 4, 4, 4,
  4, 4, 2, 4, 4, 4, 4,
  4, 4, 2, 4, 2,
  8, 8, 4, 4, 4, 2, 2,
  1
)
melody_5 = ( __melody_5, __durations_5, "Way down we go" )

#----------------------------------------------------------------------------------------
__melody_6 = (
  NOTE_B4, REST,
  NOTE_FS4, NOTE_FS4, NOTE_B4, NOTE_FS4, NOTE_E4, REST, NOTE_B3,

  NOTE_D4, NOTE_D4, NOTE_D4, NOTE_D4, NOTE_B3, NOTE_B3, NOTE_D4, NOTE_D4, NOTE_D4, NOTE_D4, NOTE_B3, NOTE_B3,
  NOTE_CS4, NOTE_CS4, NOTE_CS4, NOTE_CS4, NOTE_AS3, NOTE_AS3, NOTE_CS4, NOTE_CS4, NOTE_CS4, NOTE_CS4, NOTE_AS3, NOTE_B3,
  NOTE_D4, NOTE_D4, NOTE_D4, NOTE_D4, NOTE_B3, NOTE_B3, NOTE_D4, NOTE_D4, NOTE_D4, NOTE_D4, NOTE_B3, NOTE_B3,
  NOTE_CS4, NOTE_CS4, NOTE_CS4, NOTE_CS4, NOTE_AS3, NOTE_AS3, NOTE_CS4, NOTE_CS4, NOTE_CS4, NOTE_CS4, NOTE_AS3,

  NOTE_B4, NOTE_A4, NOTE_G4, NOTE_D4, NOTE_FS4, NOTE_E4, NOTE_B4,
  NOTE_B4, NOTE_A4, NOTE_G4, NOTE_D4, NOTE_FS4, NOTE_AS4,

  REST, NOTE_E4, NOTE_FS4, NOTE_E4, NOTE_D4, NOTE_B3,
  NOTE_D4, NOTE_E4, NOTE_D4, NOTE_E4, NOTE_D4, NOTE_E4, NOTE_D4, NOTE_E4, NOTE_D4, NOTE_E4, NOTE_B4,
  REST, NOTE_E4, NOTE_FS4, NOTE_E4, NOTE_D4, NOTE_B3,
  NOTE_D4, NOTE_E4, NOTE_D4, NOTE_E4, NOTE_D4, NOTE_E4, NOTE_B4, REST, NOTE_B3, NOTE_B3, NOTE_B3,
  NOTE_D4, NOTE_CS4, NOTE_B3, NOTE_FS3, NOTE_E3, NOTE_FS3, NOTE_FS4, NOTE_B4, NOTE_FS4, NOTE_E4,
  
  REST
)
__durations_6 = (
  4, 2,
  4, 8, 4, 8, 4, 2, 8,

  4, 4, 8, 8, 2, 8, 4, 4, 8, 8, 2, 8,
  4, 4, 8, 8, 2, 8, 4, 4, 8, 8, 2, 8,
  4, 4, 8, 8, 2, 8, 4, 4, 8, 8, 2, 8,
  4, 4, 8, 8, 2, 8, 4, 4, 8, 8, 2,

  2, 2, 2, 4, 1, 1, 8,
  2, 2, 2, 4, 1, 1,

  2, 2, 8, 8, 8, 2,
  8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 2,
  2, 2, 8, 8, 8, 2,
  8, 8, 8, 8, 8, 8, 2, 2, 8, 8, 8,
  2, 2, 2, 8, 4, 4, 8, 4, 8, 2,

  1
)
melody_6 = ( __melody_6, __durations_6, "Enemy" )

#----------------------------------------------------------------------------------------
__melody_7 = (
  NOTE_B3, NOTE_D4, NOTE_E4, NOTE_E4,
  NOTE_B3, NOTE_D4, NOTE_E4, NOTE_E4,
  NOTE_B3, NOTE_D4, NOTE_E4, NOTE_E4,

  NOTE_B3, NOTE_D4, NOTE_G4, NOTE_G4, NOTE_G4, NOTE_FS4, NOTE_E4, NOTE_D4, NOTE_E4, NOTE_E4, NOTE_D4,
  NOTE_B3,

  NOTE_G4, NOTE_G4, NOTE_FS4, NOTE_E4, NOTE_E4, NOTE_FS4,
  NOTE_G4, NOTE_FS4, NOTE_E4, NOTE_E4, NOTE_B3,
  NOTE_A3, NOTE_G3,

  REST
)
__durations_7 = (
  8, 8, 8, 8,
  8, 8, 8, 8,
  8, 8, 8, 8,

  8, 8, 8, 8, 8, 8, 8, 8, 8, 16, 16,
  1,

  8, 8, 8, 8, 4, 8,
  4, 4, 8, 4, 4,
  8, 1,

  1
)
melody_7 = ( __melody_7, __durations_7, "Livin' On A Prayer" )

#----------------------------------------------------------------------------------------
__melody_8 = (
  REST, NOTE_E5, NOTE_D5, NOTE_C5, NOTE_B4, NOTE_A4, NOTE_G4, NOTE_A4, NOTE_B4,
  NOTE_G5, NOTE_E5, NOTE_F5, NOTE_G5, NOTE_E5, NOTE_F5, NOTE_G5, REST,
  NOTE_E5, NOTE_C5, NOTE_D5, NOTE_E5, NOTE_C5, NOTE_D5, NOTE_E5, NOTE_C5, NOTE_D5, NOTE_E5, NOTE_D5, NOTE_C5,
  NOTE_A4, NOTE_A4, REST, NOTE_A4, NOTE_A4, NOTE_G4, NOTE_A4, NOTE_G4, NOTE_G4, REST, NOTE_G4,
  NOTE_A4, NOTE_A4, NOTE_A4, NOTE_A4, NOTE_C5, NOTE_B4,
  NOTE_G5, NOTE_E5, NOTE_F5, NOTE_G5, NOTE_E5, NOTE_F5, NOTE_G5,
  NOTE_E5, NOTE_C5, NOTE_D5, NOTE_E5, NOTE_C5, NOTE_D5, NOTE_E5, NOTE_C5, NOTE_D5, NOTE_E5, NOTE_D5, NOTE_C5,
  NOTE_A4, NOTE_A4, REST, NOTE_A4, NOTE_A4, NOTE_G4, NOTE_A4, NOTE_G4, NOTE_G4, REST, NOTE_G4, NOTE_G4,
  NOTE_A4, NOTE_A4, NOTE_A4, REST, NOTE_A4, NOTE_C5, NOTE_B4, NOTE_B4, NOTE_B4, NOTE_B4, NOTE_C5, REST,
  REST
)
__durations_8 = (
  4, 2, 2, 2, 2, 2, 2, 2, 4,
  4, 8, 8, 4, 8, 8, 2, 2,
  4, 8, 8, 4, 8, 8, 4, 8, 8, 4, 8, 8,
  4, 8, 8, 4, 8, 8, 8, 8, 2, 8, 8,
  8, 8, 4, 4, 4, 1,
  4, 8, 8, 4, 8, 8, 1,
  4, 8, 8, 4, 8, 8, 4, 8, 8, 4, 8, 8,
  4, 8, 8, 4, 8, 8, 8, 8, 4, 4, 8, 8,
  8, 8, 8, 8, 4, 4, 8, 8, 4, 4, 8, 8,
  1
)
melody_8 = ( __melody_8, __durations_8, "Memories" )

#----------------------------------------------------------------------------------------
__melody_9 = (
  NOTE_D5, NOTE_B5, NOTE_A5, NOTE_A5, NOTE_FS5, NOTE_D4, NOTE_FS5, NOTE_D4, NOTE_D4,
  NOTE_A5, NOTE_FS5, REST,
  NOTE_FS5, NOTE_G5, NOTE_A5, NOTE_G5, NOTE_FS5, NOTE_FS5, NOTE_FS5, REST,
  NOTE_B4, NOTE_D5, NOTE_FS5, NOTE_E5, NOTE_E5, NOTE_FS5, REST,
  NOTE_A5, NOTE_FS5, NOTE_FS5, REST,
  NOTE_FS5, NOTE_G5, NOTE_A5, NOTE_G5, NOTE_FS5, NOTE_FS5, NOTE_FS5, REST,
  NOTE_B4, NOTE_D5, NOTE_FS5, NOTE_D5, REST,

  NOTE_D5,
  NOTE_FS5, NOTE_G5, NOTE_FS5, NOTE_G5, NOTE_FS5, NOTE_G5, NOTE_A5, REST,
  NOTE_FS5, NOTE_G5, NOTE_FS5, NOTE_G5, NOTE_FS5, NOTE_B5, NOTE_A5, REST,
  NOTE_FS5, NOTE_G5, NOTE_FS5, NOTE_G5, NOTE_FS5, NOTE_D5, NOTE_E5, NOTE_D5, REST,
  NOTE_FS5, NOTE_G5, NOTE_FS5, NOTE_G5, NOTE_FS5, NOTE_A5, NOTE_A5, REST,
  NOTE_FS5, NOTE_G5, NOTE_FS5, NOTE_G5, NOTE_FS5, NOTE_B5, NOTE_A5, REST,
  NOTE_FS5, NOTE_G5, NOTE_FS5, NOTE_G5, NOTE_FS5, NOTE_D5, NOTE_E5, REST,

  REST
)
__durations_9 = (
  2, 4, 2, 4, 2, 4, 2, 1, 1,
  4, 1, 2,
  4, 4, 4, 2, 4, 4, 1, 2,
  8, 4, 4, 8, 4, 4, 2,
  4, 4, 1, 4,
  4, 4, 4, 2, 4, 4, 1, 2,
  8, 4, 2, 2, 2,

  8,
  8, 8, 8, 4, 4, 8, 2, 4,
  8, 8, 8, 8, 4, 4, 2, 4,
  8, 8, 8, 4, 4, 8, 2, 2, 4,
  8, 8, 8, 8, 4, 4, 2, 4,
  8, 8, 8, 8, 4, 4, 2, 4,
  8, 8, 8, 8, 4, 8, 2, 2,

  1
)
melody_9 = ( __melody_9, __durations_9, "It's you" )

#----------------------------------------------------------------------------------------
__melody_10 = (
  NOTE_D3, REST, NOTE_D3, REST, NOTE_D3, REST, NOTE_D3, NOTE_D3, NOTE_D3, NOTE_A2, REST,
  NOTE_D3, REST, NOTE_D3, REST, NOTE_D3, REST, NOTE_D3, NOTE_D3, NOTE_D3, NOTE_A2, REST,
  NOTE_D3, REST, NOTE_D3, REST, NOTE_D3, REST, NOTE_D3, NOTE_D3, NOTE_D3, NOTE_A2, REST,
  NOTE_D3,
  NOTE_D4, REST, NOTE_D4, NOTE_D4, REST,
  NOTE_E3, NOTE_D3, NOTE_F3, REST, NOTE_F3,
  NOTE_D4, REST, NOTE_D4, NOTE_D4, REST,
  NOTE_D3,
  NOTE_D4, REST, NOTE_D4, NOTE_D4, REST,
  NOTE_E3, NOTE_D3, NOTE_F3, REST, NOTE_F3,
  NOTE_D4,
  REST
)
__durations_10 = (
  8, 16, 8, 16, 8, 16, 10, 10, 10, 3, 2,
  8, 16, 8, 16, 8, 16, 10, 10, 10, 3, 2,
  8, 16, 8, 16, 8, 16, 10, 10, 10, 3, 2,
  4,
  4, 3, 4, 4, 3,
  6, 6, 6, 33, 6,
  4, 3, 4, 4, 3,
  4,
  4, 3, 4, 4, 3,
  6, 6, 6, 33, 6,
  3,
  1
)
melody_10 = ( __melody_10, __durations_10, "Ice Ice Baby" )

#----------------------------------------------------------------------------------------
__melody_11 = (
  REST,
  
  NOTE_D5, NOTE_D5, NOTE_E5, NOTE_FS5, NOTE_G5, NOTE_A5, NOTE_E5, NOTE_D5, NOTE_FS5, NOTE_E5, NOTE_D5, REST,
  NOTE_B5, NOTE_D5, NOTE_D5, NOTE_D5, NOTE_CS5, NOTE_B5, NOTE_A5, NOTE_B5, NOTE_CS5, NOTE_D5, NOTE_B5, NOTE_A5,
  NOTE_D5, NOTE_D5, NOTE_E5, NOTE_FS5, NOTE_G5, NOTE_A5, NOTE_E5, NOTE_D5, NOTE_FS5, NOTE_E5, NOTE_D5,
  NOTE_A5, NOTE_D5, REST, NOTE_A5, NOTE_D5, REST, NOTE_A5, NOTE_D5, REST, NOTE_A5, NOTE_D5, NOTE_B5,
  NOTE_CS5, NOTE_CS5, NOTE_CS5, NOTE_CS5, NOTE_CS5,
  NOTE_A5, NOTE_CS5, NOTE_A5, NOTE_CS5, NOTE_A5, NOTE_CS5,
  NOTE_D5, NOTE_D5, REST,
  NOTE_CS5, NOTE_CS5, NOTE_CS5,
  NOTE_D5, NOTE_CS5, NOTE_D5, NOTE_CS5, NOTE_D5, NOTE_FS5,
  NOTE_D5, NOTE_CS5, NOTE_D5, NOTE_CS5, NOTE_D5, NOTE_CS5,
  NOTE_CS5, NOTE_D5, NOTE_CS5, NOTE_D5, NOTE_CS5, NOTE_CS5,
  NOTE_D5, NOTE_CS5, NOTE_CS5, NOTE_D5, NOTE_CS5, NOTE_CS5,
  NOTE_CS5, NOTE_D5, NOTE_CS5, NOTE_CS5, NOTE_G5, NOTE_FS5,
  NOTE_D5, NOTE_E5, NOTE_E5, NOTE_E5, NOTE_D5,

  REST
)
__durations_11 = (
  4,

  4, 4, 4, 4, 4, 4, 2, 4, 4, 4, 1, 4,
  4, 4, 4, 4, 4, 4, 2, 4, 4, 4, 1, 2,
  4, 4, 4, 4, 4, 4, 2, 4, 4, 4, 4,
  4, 2, 4, 4, 2, 4, 4, 2, 4, 4, 4, 2,
  4, 4, 4, 4, 4,
  4, 4, 4, 4, 4, 4,
  4, 2, 2,
  4, 4, 4,
  4, 4, 4, 4, 4, 4,
  4, 4, 4, 4, 4, 4,
  4, 4, 4, 4, 4, 4,
  4, 4, 4, 4, 4, 4,
  4, 4, 4, 4, 4, 4,
  4, 4, 4, 4, 4,

  1
)
melody_11 = ( __melody_11, __durations_11, "End of Beginning" )

#----------------------------------------------------------------------------------------
__melody_12 = (
  NOTE_CS4, NOTE_E4, NOTE_CS4, NOTE_CS4, NOTE_E4,
  NOTE_CS4, NOTE_CS4, NOTE_E4, NOTE_CS4, NOTE_DS4,
  NOTE_CS4, NOTE_CS4, NOTE_E4, NOTE_CS4,
  NOTE_B3,
  NOTE_CS4, NOTE_E4, NOTE_CS4, NOTE_CS4, NOTE_E4,
  NOTE_CS4, NOTE_DS4, NOTE_CS4, NOTE_E4,
  NOTE_B3,
  NOTE_E4, NOTE_E4, NOTE_E4, NOTE_E4, NOTE_E4, NOTE_E4, NOTE_E4, NOTE_E4, NOTE_E4,
  NOTE_E4, NOTE_E4, NOTE_E4, NOTE_E4, NOTE_FS4, NOTE_GS4, NOTE_GS4,
  NOTE_GS4, NOTE_E4, NOTE_FS4, NOTE_B4, NOTE_GS4, NOTE_GS4, NOTE_GS4, NOTE_GS4, NOTE_GS4,
  NOTE_FS4, NOTE_FS4, NOTE_FS4, NOTE_GS4, NOTE_FS4, NOTE_FS4, NOTE_FS4, NOTE_FS4, NOTE_FS4, NOTE_GS4, NOTE_FS4,
  NOTE_E4, NOTE_CS4, NOTE_CS4, NOTE_GS4, NOTE_GS4,
  NOTE_GS4, NOTE_GS4, NOTE_GS4, NOTE_GS4, NOTE_GS4, NOTE_GS4, NOTE_GS4, NOTE_GS4, NOTE_GS4,
  NOTE_GS4, NOTE_B4, NOTE_GS4, NOTE_GS4, NOTE_FS4, NOTE_FS4, NOTE_E4, NOTE_GS4,
  NOTE_FS4, NOTE_E4, NOTE_E4, NOTE_E4, NOTE_B4, NOTE_GS4, NOTE_GS4, NOTE_GS4, NOTE_FS4,
  NOTE_FS4, NOTE_FS4, NOTE_FS4, NOTE_FS4, NOTE_FS4, NOTE_FS4, NOTE_FS4, NOTE_FS4,
  NOTE_E4, NOTE_CS4, NOTE_CS4, NOTE_CS4, NOTE_CS4, NOTE_CS4,
  NOTE_GS3, NOTE_B3,
  NOTE_CS4, NOTE_CS4, NOTE_FS4, NOTE_GS4, NOTE_E4, NOTE_FS4,
  NOTE_B3,
  NOTE_E4, NOTE_FS4, NOTE_GS4, NOTE_FS4, NOTE_E4, NOTE_CS4, NOTE_E4, NOTE_GS4,
  NOTE_FS4, NOTE_E4, NOTE_FS4, NOTE_CS4, NOTE_B4, NOTE_GS4, NOTE_GS4, NOTE_FS4, NOTE_FS4,
  NOTE_E4, NOTE_CS4, NOTE_E4, NOTE_FS4, NOTE_GS4, NOTE_FS4, NOTE_E4,
  NOTE_FS4, NOTE_E4, NOTE_CS4, NOTE_CS4,
  NOTE_B3,
  NOTE_CS4, NOTE_CS4, NOTE_FS4, NOTE_GS4, NOTE_E4, NOTE_FS4, NOTE_FS4,
  NOTE_B3,
  NOTE_FS4, NOTE_GS4, NOTE_FS4, NOTE_E4, NOTE_CS4, NOTE_E4, NOTE_GS4, NOTE_FS4,
  NOTE_E4, NOTE_FS4, NOTE_CS4, NOTE_B4, NOTE_GS4, NOTE_GS4, NOTE_FS4, NOTE_FS4, NOTE_E4,
  NOTE_CS4, NOTE_B4, NOTE_GS4, NOTE_GS4, NOTE_FS4, NOTE_FS4, NOTE_E4,
  NOTE_CS4, NOTE_CS4,
  NOTE_GS3, NOTE_B3,
  NOTE_E4, NOTE_FS4, NOTE_GS4, NOTE_FS4, NOTE_E4, NOTE_E4, NOTE_E4, NOTE_FS4, NOTE_FS4,
  NOTE_E4, NOTE_FS4, NOTE_GS4, NOTE_FS4, NOTE_E4, NOTE_E4, NOTE_E4, NOTE_FS4|
  NOTE_CS4, NOTE_E4, NOTE_FS4, NOTE_GS4, NOTE_CS4,
  NOTE_E4, NOTE_E4, NOTE_FS4, NOTE_FS4, NOTE_E4, NOTE_FS4, NOTE_GS4,
  NOTE_FS4, NOTE_E4, NOTE_E4, NOTE_FS4, NOTE_CS4, NOTE_CS4,
  NOTE_FS4, NOTE_GS4, NOTE_B4, NOTE_GS4, NOTE_FS4, NOTE_E4, NOTE_E4, NOTE_FS4,
  NOTE_E4, NOTE_FS4, NOTE_GS4, NOTE_FS4, NOTE_E4, NOTE_E4, NOTE_FS4,
  NOTE_CS4, NOTE_CS4, NOTE_CS4, NOTE_CS4, NOTE_CS4, NOTE_E4, NOTE_FS4, NOTE_GS4, NOTE_CS4, NOTE_E4,
  NOTE_FS4, NOTE_E4, NOTE_FS4, NOTE_E4, NOTE_FS4, NOTE_GS4,
  NOTE_FS4, NOTE_E4, NOTE_E4, NOTE_FS4, NOTE_CS4, NOTE_CS4, NOTE_CS4, NOTE_E4, NOTE_E4,
  NOTE_FS4, NOTE_FS4, NOTE_GS4, NOTE_GS4,
  NOTE_E4, NOTE_FS4, NOTE_GS4, NOTE_FS4, NOTE_E4, NOTE_E4, NOTE_FS4, NOTE_CS4, NOTE_CS4,
  NOTE_CS4, NOTE_E4, NOTE_E4, NOTE_FS4, NOTE_FS4, NOTE_GS4,
  NOTE_GS4, NOTE_E4, NOTE_FS4, NOTE_GS4, NOTE_FS4,
  NOTE_E4, NOTE_E4, NOTE_FS4, NOTE_CS4, NOTE_CS4, NOTE_CS4, NOTE_E4, NOTE_E4,
  NOTE_FS4, NOTE_FS4, NOTE_GS4, NOTE_GS4,
  NOTE_E4, NOTE_FS4, NOTE_GS4, NOTE_FS4, NOTE_E4, NOTE_E4, NOTE_FS4, NOTE_CS4, NOTE_CS4,
  NOTE_CS4, NOTE_CS4, NOTE_CS4, NOTE_CS4, NOTE_E4, NOTE_FS4, NOTE_GS4, NOTE_CS4, NOTE_E4, NOTE_FS4,
  NOTE_CS4,
)
__durations_12 = (
  2,2,4,2,2,4,2,2,4,2,2,2,2,2,2,2,2,4,2,2,4,
  2,2,2,2,8,8,4,4,8,8,8,8,8,8,8,2,8,8,4,2,8,
  8,4,8,8,8,4,4,8,8,8,8,8,4,8,4,8,8,8,8,4,2,
  8,8,8,8,4,8,8,8,8,8,8,2,8,4,8,8,8,8,8,2,4,
  8,8,2,4,8,8,8,8,8,8,2,8,8,4,4,4,8,8,2,4,4,
  2,4,2,2,4,8,8,8,2,2,8,4,8,4,4,4,4,8,8,8,8,
  2,8,8,4,8,8,4,2,8,4,8,4,4,4,4,2,2,2,2,4,8,
  8,8,2,2,2,4,8,4,4,4,4,8,8,8,8,2,8,8,4,8,8,
  4,2,8,8,4,8,8,4,2,2,4,2,8,8,4,8,8,4,8,8,2,
  8,8,4,8,8,4,8,8,2,8,8,4,4,4,8,8,2,8,8,4,8,
  8,8,4,8,2,4,4,8,8,4,4,8,2,8,8,4,4,4,8,8,4,
  8,8,8,8,8,8,4,4,4,4,8,2,8,8,4,8,8,8,4,8,4,
  4,4,4,4,4,4,2,8,8,4,8,8,8,4,8,4,4,4,4,4,4,
  4,2,8,8,4,8,8,8,4,8,4,4,4,4,4,4,4,2,8,8,4,
  8,8,8,4,8,4,8,8,8,8,8,8,4,4,4,4,2
)
melody_12 = ( __melody_12, __durations_12, "Shape of you" )

#----------------------------------------------------------------------------------------
__melody_13 = (
  NOTE_DB3, NOTE_EB3, NOTE_DB3, REST, NOTE_E3, NOTE_FS3, NOTE_E3, REST,
  NOTE_DB3, NOTE_EB3, NOTE_DB3, REST, NOTE_A2, REST, NOTE_A2, REST,
  NOTE_DB3, NOTE_EB3, NOTE_DB3, REST, NOTE_E3, NOTE_FS3, NOTE_E3, REST,
  NOTE_DB3, NOTE_EB3, NOTE_DB3, REST, NOTE_A2,
  NOTE_DB3, NOTE_DB3, NOTE_EB3, NOTE_DB3, REST, NOTE_E3, NOTE_E3, NOTE_FS3, NOTE_E3,
  NOTE_DB3, REST, NOTE_DB3, NOTE_EB3, NOTE_DB3, REST, NOTE_A2, NOTE_A2, REST,
  NOTE_DB3, REST, NOTE_DB3, NOTE_EB3, NOTE_DB3, REST, NOTE_E3, REST, NOTE_E3, NOTE_FS3, NOTE_E3, REST,
  NOTE_DB3, REST, NOTE_DB3, NOTE_EB3, NOTE_DB3, REST, NOTE_A2, REST,
  NOTE_DB3, REST, NOTE_DB3, NOTE_EB3, NOTE_DB3, REST, NOTE_E3, REST, NOTE_E3, NOTE_FS3, NOTE_E3, REST,
  NOTE_DB3, REST, NOTE_DB3, NOTE_EB3, NOTE_DB3, REST, NOTE_A2, REST,
  NOTE_DB3, REST, NOTE_DB3, NOTE_EB3, NOTE_DB3, REST, NOTE_E3, REST, NOTE_E3, NOTE_FS3, NOTE_E3, REST,
  NOTE_DB3, REST, NOTE_DB3, NOTE_EB3, NOTE_DB3, REST, NOTE_A2, REST,
  NOTE_DB3, REST, NOTE_DB3, REST, NOTE_DB3, REST, NOTE_DB3, REST, NOTE_DB3, REST, NOTE_DB3, REST,
  NOTE_EB3, REST, NOTE_EB3, REST, NOTE_EB3, REST, NOTE_EB3, REST, NOTE_EB3, REST, NOTE_EB3, REST,
  NOTE_B2, REST, NOTE_B2, REST, NOTE_B2, REST, NOTE_B2, REST, NOTE_B2, REST, NOTE_B2, REST,
  NOTE_B2, REST, NOTE_B2, REST, NOTE_B2, REST, NOTE_B2, REST, NOTE_B2, REST, NOTE_B2, REST,
)
__durations_13 = (
  4, 16, 8, 16, 4, 16, 8, 16,
  4, 16, 8, 16, 4, 16, 8, 16,
  4, 16, 16, 8, 4, 16, 8, 16,
  4, 16, 16, 8, 2,
  8, 8, 16, 16, 8, 8, 8, 16, 16, 8,
  16, 16, 8, 16, 16, 8, 4, 8, 8,
  16, 16, 8, 16, 16, 8, 16, 16, 16, 16, 8, 8,
  16, 16, 8, 16, 16, 8, 4, 4,
  16, 16, 8, 16, 16, 8, 16, 16, 16, 16, 8, 8,
  16, 16, 8, 16, 16, 8, 4, 4,
  16, 16, 8, 16, 16, 8, 16, 16, 16, 16, 8, 8,
  16, 16, 8, 16, 16, 8, 4, 4,
  8, 16, 16, 16, 16, 8, 8, 16, 16, 16, 16, 8,
  8, 16, 16, 16, 16, 8, 8, 16, 16, 16, 16, 8,
  8, 16, 16, 16, 16, 8, 8, 16, 16, 16, 16, 8,
  8, 16, 16, 16, 16, 8, 8, 16, 16, 16, 16, 8,
)
melody_13 = ( __melody_13, __durations_13, "The Red" )

#----------------------------------------------------------------------------------------
__melody_14 = (
  NOTE_E4, NOTE_F4, NOTE_G4, NOTE_E5, NOTE_C5, NOTE_D5, NOTE_C5, NOTE_C5, NOTE_B4, NOTE_B4, NOTE_D4,
  NOTE_E4, NOTE_F4, NOTE_D5, NOTE_B4, NOTE_C5, NOTE_B4, NOTE_A4, NOTE_G4, NOTE_G4, NOTE_E4, NOTE_F4, 
  NOTE_G4, NOTE_C5, NOTE_D5, NOTE_E5, NOTE_D5, NOTE_C5, NOTE_A4, NOTE_D5, NOTE_E5, NOTE_F5, NOTE_E5, 
  NOTE_D5, NOTE_G4, NOTE_F5, NOTE_E5, NOTE_D5, NOTE_C5, NOTE_C5, REST, NOTE_C5, REST, NOTE_C5, NOTE_E5, 
  NOTE_C5, NOTE_D5, REST, NOTE_D5, NOTE_D5, NOTE_D5, REST, NOTE_D5, NOTE_F5, NOTE_D5, NOTE_E5, REST, NOTE_E5, 
  NOTE_E5, NOTE_E5, REST, NOTE_E5, NOTE_G5, NOTE_E5, NOTE_F5, REST, NOTE_F5, NOTE_F5, NOTE_E5, NOTE_D5, NOTE_G4, 
  NOTE_B4, NOTE_C5, NOTE_C5, REST
)
__durations_14 = (
  8, 8, 4, 4, 4, 8, 8, 4, 4, 4, 8, 8, 4, 4, 4, 8, 8, 4, 4, 4, 8, 8, 4, 8, 8, 4, 8, 8, 4, 
  8, 8, 4, 8, 8, 4, 4, 4, 4, 2, 4, 4, 4, 8, 8, 4, 4, 4, 8, 8, 2, 4, 8, 8, 4, 4, 4, 8, 8, 
  2, 4, 8, 8, 4, 4, 4, 8, 8, 4, 8, 8, 2, 2, 2, 4, 4
)
melody_14 = ( __melody_14, __durations_14, "It's a small world" )

#----------------------------------------------------------------------------------------
__melody_15 = (
  REST,

  NOTE_E4, NOTE_GS4, NOTE_CS4,
  NOTE_E4, NOTE_GS4, NOTE_CS4, NOTE_GS4,

  NOTE_E4, NOTE_GS4, NOTE_CS4,
  NOTE_E4, NOTE_GS4, NOTE_CS4, NOTE_B4,

  NOTE_E4, NOTE_CS4, NOTE_E4, NOTE_GS4, NOTE_B4, NOTE_DS4, NOTE_E4,
  NOTE_CS4, NOTE_B5, NOTE_A5, NOTE_GS4, REST,

  NOTE_E4, NOTE_CS4, NOTE_E4, NOTE_GS4, NOTE_B4, NOTE_DS4, NOTE_E4,
  NOTE_CS4, NOTE_B5, NOTE_A5, NOTE_CS5, REST,

  NOTE_E4, NOTE_CS4, NOTE_E4, NOTE_GS4, NOTE_B4, NOTE_DS4, NOTE_E4,
  NOTE_CS4, NOTE_B5, NOTE_A5, NOTE_CS5, REST,

  NOTE_A5, NOTE_GS4, NOTE_CS4, NOTE_GS4,
  NOTE_A5, NOTE_GS4, NOTE_CS4, NOTE_GS4,
  NOTE_A5, NOTE_GS4, NOTE_CS4, NOTE_GS4,
  NOTE_A5, NOTE_GS4, NOTE_CS4, NOTE_GS4,
  NOTE_A5, NOTE_GS4, NOTE_CS4, NOTE_GS4,

  REST
)
__durations_15 = (
  4,

  2, 3, 1,
  2, 3, 1, 3,

  2, 3, 1,
  2, 3, 1, 3,

  3, 6, 6, 6, 6, 6, 6,
  4, 3, 3, 3, 2,

  3, 6, 6, 6, 6, 6, 6,
  4, 3, 3, 3, 2,

  3, 6, 6, 6, 6, 6, 6,
  4, 3, 3, 3, 2,

  4, 8, 8, 8,
  4, 8, 8, 8,
  4, 8, 8, 8,
  4, 8, 8, 8,
  4, 8, 8, 8,

  1
)
melody_15 = ( __melody_15, __durations_15, "First Day Out" )

#----------------------------------------------------------------------------------------
__melody_16 = (
  NOTE_A4, NOTE_C5, NOTE_D5, NOTE_E5, NOTE_E5, NOTE_F5, NOTE_D5, NOTE_E5, REST,
  NOTE_D5, NOTE_D5, NOTE_C5, NOTE_B4, NOTE_C5, NOTE_A4, REST, NOTE_A4,
  NOTE_D5, NOTE_D5, NOTE_C5, NOTE_B4,
  NOTE_D5, NOTE_D5, NOTE_C5, NOTE_B4,
  NOTE_C5, NOTE_A4, REST, NOTE_G4, NOTE_A4,
)
__durations_16 = (
  4, 4, 4, 3, 3, 4, 4, 2, 4,
  4, 6, 6, 6, 2, 3, 8, 4,
  4, 4, 4, 4,
  4, 6, 6, 6,
  2, 3, 8, 2, 1
)
melody_16 = ( __melody_16, __durations_16, "Was wollen wir trinken" )

#----------------------------------------------------------------------------------------
__melody_17 = (
  REST,

  NOTE_E4, NOTE_DS4, NOTE_B3, NOTE_E4, NOTE_DS4, NOTE_B3,
  NOTE_E4, NOTE_DS4, NOTE_B3, NOTE_E4, NOTE_FS4, NOTE_GS4,
  NOTE_B4, NOTE_CS5, NOTE_E5, NOTE_A5, NOTE_GS5, NOTE_FS5,
  NOTE_D5, NOTE_D5, NOTE_E5, NOTE_FS5, NOTE_E5,
  NOTE_B4, NOTE_GS4, NOTE_A5, NOTE_B4,
  NOTE_DS5, NOTE_E5,
  NOTE_B4, NOTE_CS5, NOTE_E5, NOTE_A5, NOTE_GS5,
  NOTE_DS5,
  NOTE_B5, NOTE_A5, NOTE_GS5,

  NOTE_E5, NOTE_E5, NOTE_E5, NOTE_FS5, NOTE_FS5, NOTE_FS5,
  NOTE_GS5, NOTE_GS5, NOTE_GS5, NOTE_DS5, NOTE_DS5, NOTE_DS5,

  NOTE_CS5, NOTE_E4, NOTE_CS5, NOTE_B4,
  NOTE_CS5, NOTE_B4, NOTE_GS4, NOTE_A4,
  NOTE_B4, NOTE_A4, NOTE_GS4, NOTE_E4,
  NOTE_E4
)
__durations_17 = (
  4,

  4, 4, 4, 4, 4, 4,
  4, 4, 4, 4, 4, 4,
  4, 4, 4, 4, 4, 4,
  2, 4, 4, 4, 4,
  2, 4, 4, 4,
  2, 2,
  4, 4, 4, 4, 4,
  2,
  4, 4, 4,

  4, 4, 4, 4, 4, 4,
  4, 4, 4, 4, 4, 4,

  2, 4, 2, 4,
  2, 2, 4, 4,
  2, 2, 4, 4,
  1,
)
melody_17 = ( __melody_17, __durations_17, "Blue" )

#########################################################################################
songs = { 
    melody_1[NAME]:melody_1,
    melody_2[NAME]:melody_2,
    melody_3[NAME]:melody_3,
    melody_4[NAME]:melody_4,
    melody_5[NAME]:melody_5,
    melody_6[NAME]:melody_6,
    melody_7[NAME]:melody_7,
    melody_8[NAME]:melody_8,
    melody_9[NAME]:melody_9,
    melody_10[NAME]:melody_10,
    melody_11[NAME]:melody_11,
    melody_12[NAME]:melody_12,
    melody_13[NAME]:melody_13,
    melody_14[NAME]:melody_14,
    melody_15[NAME]:melody_15,
    melody_16[NAME]:melody_16,
    melody_17[NAME]:melody_17,
}