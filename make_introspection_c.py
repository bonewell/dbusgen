#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @file make_introspection_c.py
#  @brief Converts introspection.xml to C-string
#
# This file is a part of HMI D-Bus layer.
#
# Copyright (c) 2013-2016, Ford Motor Company
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following
# disclaimer in the documentation and/or other materials provided with the
# distribution.
#
# Neither the name of the Ford Motor Company nor the names of its contributors
# may be used to endorse or promote products derived from this software
# without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR 'A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from argparse import ArgumentParser
from xmladapter import XMLAdapter
from protocol import Protocol
from DBusIntrospectionVisitor import DBusIntrospectionVisitor
from BinaryIntrospection import BinaryIntrospection

arg_parser = ArgumentParser(description="Converts introspection.xml to C-string")
arg_parser.add_argument('--infile', required=True, help="Full name of input file, e.g. sdl/src/components/interfaces/QT_HMI_API.xml")
arg_parser.add_argument('--outdir', required=True, help="Path to directory where output file introspection_xml.cc will be saved")
args = arg_parser.parse_args()

adapter = XMLAdapter(args.infile)
visitor = DBusIntrospectionVisitor('sdl', 'com.ford.hmi', '/com/ford/hmi')
print("Read protocol from %s" % args.infile)
Protocol(adapter).accept(visitor)
print("Save binary introspection to %s" % args.outdir)
BinaryIntrospection(visitor).save(args.outdir)
