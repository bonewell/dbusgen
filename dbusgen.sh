#!/usr/bin/env bash

mode=$1

case "$mode" in
    test) python make_for_test.py --infile QT_HMI_API.xml ;;
    test3) python3 make_for_test.py --infile QT_HMI_API.xml ;;
    desc) python make_message_descriptions.py --infile QT_HMI_API.xml --outdir output ;;
    intro) python make_introspection_c.py --infile QT_HMI_API.xml --outdir output ;;
    qml) python make_qml_dbus_qml.py --infile QT_HMI_API.xml --version 5.1.0 --outdir output ;;
    cpp) python make_qml_dbus_cpp.py --infile QT_HMI_API.xml --version 5.1.0 --outdir output ;;
    request) python make_request_to_sdl.py --infile QT_HMI_API.xml --version 5.1.0 --outdir output ;;
    response) python make_hmi_requests.py --infile QT_HMI_API.xml --version 5.1.0 --outdir output ;;
    notify) python make_notifications_qml.py --infile QT_HMI_API.xml --version 5.1.0 --outdir output ;;
esac
