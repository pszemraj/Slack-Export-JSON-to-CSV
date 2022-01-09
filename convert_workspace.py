"""
convert_workspace.py - uses subprocess to convert a slack workspace to a csv file

"""
import argparse


def get_parser():

    """

    get_parser - a helper function for the argparse module

    """

    parser = argparse.ArgumentParser(
        description="convert_workspace.py - converts a slack workspace to a csv file using original slack export format",
    )

    parser.add_argument(
        "-i",
        "--input-dir",
        required=True,
        type=str,
        help="enter the directory of the slack workspace when the archive was downloaded + extracted",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        required=False,
        type=str,
        default=None, # by default, output will be in the same directory as the input
        help="enter the directory where you want the csv file to be saved",
    )
    parser.add_argument(
        "--users-path",
        required=True,
        type=str,
        help="enter the directory where you want the csv file to be saved",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        required=False,
        default=False,
        action="store_true",
        help="increase output verbosity",
    )


if __name__ == "__main__":

    args = get_parser().parse_args()
