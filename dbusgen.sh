#!/usr/bin/env bash

mode=$1
old=$2
ver=$3

if [ "$old" == "old" ]; then
    dir="output"
    suffix="_old"
else
    dir="new_output"
    suffix=""
fi
case "$mode" in
    desc) python$ver make_message_descriptions"$suffix".py --infile QT_HMI_API.xml --outdir $dir ;;
    intro) python$ver make_introspection_c"$suffix".py --infile QT_HMI_API.xml --outdir $dir ;;
    qml) python$ver make_qml_dbus_qml"$suffix".py --infile QT_HMI_API.xml --version 5.1.0 --outdir $dir ;;
    cpp) python$ver make_qml_dbus_cpp"$suffix".py --infile QT_HMI_API.xml --version 5.1.0 --outdir $dir ;;
    request) python$ver make_request_to_sdl"$suffix".py --infile QT_HMI_API.xml --version 5.1.0 --outdir $dir ;;
    response) python$ver make_hmi_requests"$suffix".py --infile QT_HMI_API.xml --version 5.1.0 --outdir $dir ;;
    notify) python$ver make_notifications_qml"$suffix".py --infile QT_HMI_API.xml --version 5.1.0 --outdir $dir ;;
esac
