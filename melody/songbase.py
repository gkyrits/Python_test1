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
melody_1 = ( __melody_1, __durations_1, "Crystal Castles - Kerosene" )

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


###############################################################################
songs = { 
    melody_1[NAME]:melody_1,
    melody_2[NAME]:melody_2,
    melody_3[NAME]:melody_3,
    melody_4[NAME]:melody_4,
}