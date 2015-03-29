#!/usr/bin/env bash

python make_message_descriptions.py --infile QT_HMI_API.xml --outdir output

python make_introspection_c.py --infile QT_HMI_API.xml --outdir output

python make_qml_dbus_qml.py --infile QT_HMI_API.xml --version 5.1.0 --outdir output

python make_qml_dbus_cpp.py --infile QT_HMI_API.xml --version 5.1.0 --outdir output

python make_request_to_sdl.py --infile QT_HMI_API.xml --version 5.1.0 --outdir output

python make_hmi_requests.py --infile QT_HMI_API.xml --version 5.1.0 --outdir output

python make_notifications_qml.py --infile QT_HMI_API.xml --version 5.1.0 --outdir output
