#!/usr/bin/env python

from argparse import ArgumentParser
from XMLAdapter import XMLAdapter
from protocol.Protocol import Protocol
from DBusIntrospectionVisitor import DBusIntrospectionVisitor
arg_parser = ArgumentParser(description="Make something")
arg_parser.add_argument('--infile', required=True, help="Full name of input file, e.g. sdl/src/components/interfaces/QT_HMI_API.xml")
args = arg_parser.parse_args()

adapter = XMLAdapter(args.infile)
protocol = Protocol(adapter)
introspection = DBusIntrospectionVisitor('sdl', 'com.ford.hmi', '/com/ford/hmi')
protocol.accept(introspection)
print(introspection.xml('SDL'))
