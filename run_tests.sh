#!/usr/bin/env bash

python -m unittest -v TestXMLAdapter
python3 -m unittest -v TestProtocol
python3 -m unittest -v TestDBusIntrospectionVisitor
python3 -m unittest -v TestMessageDescriptionVisitor
