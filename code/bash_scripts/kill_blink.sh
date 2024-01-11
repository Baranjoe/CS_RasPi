#!/bin/bash

# Wird verwendet, da blink1-tool Prozesse beim aufrufen des nächsten Befehls weiter ausgeführt wurden

for pid in $(pgrep -f blink1-tool); do
    kill -9 $pid
done
