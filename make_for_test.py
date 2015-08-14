#!/usr/bin/env python

from argparse import ArgumentParser
from XMLAdapter import XMLAdapter
from protocol.Protocol import Protocol
from DBusIntrospectionVisitor import DBusIntrospectionVisitor
arg_parser = ArgumentParser(description="Make something")
arg_parser.add_argument('--infile', required=True, help="Full name of input file, e.g. sdl/src/components/interfaces/QT_HMI_API.xml")
args = arg_parser.parse_args()

xml = XMLAdapter(args.infile)
proto = Protocol(xml)
v = DBusIntrospectionVisitor('sdl', 'com.ford.hmi', '/com/ford/hmi')
proto.accept(v)
print(v.xml())
