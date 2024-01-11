#!/bin/bash

# Beendung laufender blink1-tool Prozesse
pkill -9 blink1-tool

# Sleep Pattern 1 (Blaues pulsierendes Licht)

# Länge jeder Phase definieren (in Millisekunden)
fade_duration=1000
blink_duration=2000
num_blinks=9999

# Blink Command ausführen
/home/baranjoe/blink1-tool --rgb 0,0,255 -m $fade_duration --blink $num_blinks -t $blink_duration
