#!/bin/bash

# Beendung laufender blink1-tool Prozesse
pkill -9 blink1-tool

# Sleep Pattern 2 (Bunte Farben)

# Farbpalette definieren
colors=( "255,0,0" "0,255,0" "0,0,255" "255,255,0" "0,255,255" "255,0,255" )

# Setzen jeder Farbe in der Palette
for i in "${!colors[@]}"; do
    /home/baranjoe/blink1-tool --setpattline $i --rgb ${colors[$i]}
done

# Pattern auf dem Gerät speichern
/home/baranjoe/blink1-tool --savepattern

# Pattern abspielen
/home/baranjoe/blink1-tool --play 1
