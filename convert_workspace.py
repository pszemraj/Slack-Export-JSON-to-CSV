"""
convert_workspace.py - uses subprocess to convert a slack workspace to a csv file

"""
import argparse
from pathlib import Path
import logging
import subprocess
import pandas as pd

def aggregate_CSVs(csv_dir: Path, csv_out: Path, output_file_type:str="excel"):
    """
    aggregate_CSVs - aggregates all csv files in a directory into a single csv file
    """
    csv_files = [f for f in csv_dir.iterdir() if f.is_file() and f.suffix == ".csv"]
    df = pd.DataFrame()
    for csv_file in csv_files:
        df = df.append(pd.read_csv(csv_file))
    df.to_csv(csv_out, index=False)



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
        required=False,
        type=str,
        default=None,
        help="enter path to users.json file if location is different than the default",
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
    # intialize logging
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )
    # get the arguments
    args = get_parser().parse_args()

    # process args
    input_dir = Path(args.input_dir)
    output_dir = args.output_dir
    users_path = args.users_path
    verbose = args.verbose

    output_dir = Path(output_dir) if output_dir else input_dir.parent / "converted"
    output_dir.mkdir(exist_ok=True)
    users_path = Path(users_path) if users_path else input_dir / "users.json"

    channels = [ch for ch in input_dir.iterdir() if ch.is_dir()]
    logging.info(f"found {len(channels)} channels")

    # iterate through each found channel and convert it to a csv file
    for channel in channels:
        logging.info(f"converting channel {channel.name}")
        subprocess.run(
            [
                "python3",
                "slack_json_to_csv.py",
                "-i",
                str(channel),
                "-o",
                str(output_dir),
                "--users-path",
                str(users_path),
            ],
            check=True,
        )


