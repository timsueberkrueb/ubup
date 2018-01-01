#!/bin/bash

# Require root access
if [ "$UID" -ne 0 ]; then
    # Use -E to preserve the environment (e.g. $SNAP)
    exec sudo -E "$0" "$@"
fi

# Perform setup
u="$SUDO_USER"; if [ -z "$u" ]; then u="$USER"; fi
sudo -E -u "$u" $SNAP/usr/bin/python3 $SNAP/app/main.py $@
