#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @file make_hmi_requests.py
#  @brief Generates C++ code to D-Bus adaptor on HMI side
#
# This file is a part of HMI D-Bus layer.
#
# Copyright (c) 2013-2015, Ford Motor Company
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
from os import path
from xmladapter import XMLAdapter
from protocol import Protocol
from HmiRequestsVisitor import HmiRequestsVisitor
from HmiRequests import HmiRequests

arg_parser = ArgumentParser(description="Generates C++ code to D-Bus adaptor on HMI side")
arg_parser.add_argument('--infile', required=True, help="full name of input file, e.g. applink/src/components/interfaces/QT_HMI_API.xml")
# TODO(KKolodiy): unused argument 'version', CMakeList.txt run this script with version
arg_parser.add_argument('--version', required=False, help="Qt version 4.8.5 (default) or 5.1.0")
arg_parser.add_argument('--outdir', required=True, help="path to directory where output files hmi_requests.h, hmi_requests.cc will be saved")
args = arg_parser.parse_args()

adapter = XMLAdapter(args.infile)
protocol = Protocol(adapter)
print("Read protocol: %s" % args.infile)
visitor = HmiRequestsVisitor()
visitor.logs = True
protocol.accept(visitor)
if not path.isdir(args.outdir):
    os.makedirs(args.outdir)
print("Write HMI requests")
writer = HmiRequests(visitor)
headername = path.join(args.outdir, 'hmi_requests.h')
writer.writeHeader(headername)
sourcename = path.join(args.outdir, 'hmi_requests.cc')
writer.writeSource(sourcename)
