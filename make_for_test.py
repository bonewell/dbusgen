#!/usr/bin/env python

from argparse import ArgumentParser
from XMLAdapter import XMLAdapter
from protocol.Protocol import Protocol
from DBusIntrospectionVisitor import DBusIntrospectionVisitor
from BinaryIntrospection import BinaryIntrospection

arg_parser = ArgumentParser(description="Make something")
arg_parser.add_argument('--infile', required=True, help="Full name of input file, e.g. sdl/src/components/interfaces/QT_HMI_API.xml")
arg_parser.add_argument('--outdir', required=True, help="Path to directory where output file introspection_xml.cc will be saved")
args = arg_parser.parse_args()

adapter = XMLAdapter(args.infile)
protocol = Protocol(adapter)
introspection = DBusIntrospectionVisitor('sdl', 'com.ford.hmi', '/com/ford/hmi')
protocol.accept(introspection)
binary = BinaryIntrospection(introspection)
binary.write(args.outdir + '/introspection_xml.cc')
