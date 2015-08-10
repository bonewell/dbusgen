from argparse import ArgumentParser
from XMLAdapter import XMLAdapter

arg_parser = ArgumentParser(description="Make something")
arg_parser.add_argument('--infile', required=True, help="Full name of input file, e.g. sdl/src/components/interfaces/QT_HMI_API.xml")
args = arg_parser.parse_args()

xml = XMLAdapter(args.infile)
for i in xml.interfaces():
    print i.name
