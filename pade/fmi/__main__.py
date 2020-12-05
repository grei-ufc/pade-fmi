import os
import argparse
import pade.fmi
from pythonfmu.builder import FmuBuilder

from .__version__ import __version__

def main():
    parser = argparse.ArgumentParser(prog='pade-fmi')
    parser.add_argument('-v', '--version', action='version', version=__version__)

    parser.add_argument('project_files', metavar='filename', type=str, nargs='+',
                        help='File containing FMU settings')
    parser.add_argument(
        '-d', '--dest', dest='dest', help='Where to save the FMU.', default='.'
    )

    args = parser.parse_args()

    FmuBuilder.build_FMU(
        script_file=pade.fmi.fmi_wrapper.__file__,
        dest=args.dest,
        project_files=args.project_files +
        [os.path.join(os.path.dirname(__file__), 'requirements.txt')],
        needsExecutionTool=False
    )
