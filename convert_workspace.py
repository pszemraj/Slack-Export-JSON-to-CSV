"""
convert_workspace.py - uses subprocess to convert a slack workspace to a csv file

"""
import argparse
from datetime import datetime
from pathlib import Path
import logging
import subprocess
import pandas as pd
from tqdm.auto import tqdm

logdir = Path.cwd() / "logs"
logdir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename="./out/conversion_logs.csv",
    level=logging.INFO,
    datefmt="%m/%d/%Y %I:%M:%S %p",
)


def aggregate_CSVs(csv_dir: Path, output_loc: Path, output_file_type: str = "excel"):
    """
    aggregate_CSVs - aggregates all csv files in a directory into a single csv file
    """
    csv_files = [f for f in csv_dir.iterdir() if f.is_file() and f.suffix == ".csv"]
    df = pd.DataFrame()
    for csv_file in csv_files:
        df = df.append(pd.read_csv(csv_file))

    agg_name = f"aggregated_{csv_dir.name}{datetime.now().strftime('%Y%m%d%H%M%S')}"

    if output_file_type == "excel":
        agg_loc = output_loc.parent / f"{agg_name}.xlsx"
        df.to_excel(agg_loc, index=False)
    elif output_file_type == "csv":
        agg_loc = output_loc.parent / f"{agg_name}.csv"
        df.to_csv(agg_loc, index=False)
    elif output_file_type == "feather":
        agg_loc = output_loc.parent / f"{agg_name}.ftr"
        df.to_feather(agg_loc)
    else:
        raise ValueError(
            f"{output_file_type} is not a valid output file type. Please use 'excel', 'csv', or 'feather'"
        )

    print(f"{agg_loc} created")


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
        default=None,  # by default, output will be in the same directory as the input
        help="enter the directory where you want the csv file to be saved",
    )
    parser.add_argument(
        "-u",
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
    parser.add_argument(
        "-t",
        "--output-file-type",
        required=False,
        default="excel",
        type=str,
        help="enter the type of file you want to save the output as. Default is excel. other options are csv, and feather",
    )

    return parser


if __name__ == "__main__":

    # get the arguments
    args = get_parser().parse_args()

    # process args
    input_dir = Path(args.input_dir)
    output_dir = args.output_dir
    users_path = args.users_path
    verbose = args.verbose
    merged_type = args.output_file_type

    output_dir = Path(output_dir) if output_dir else input_dir.parent / "converted"
    output_dir.mkdir(exist_ok=True)
    users_path = Path(users_path) if users_path else input_dir / "users.json"

    channels = [ch for ch in input_dir.iterdir() if ch.is_dir()]
    logging.info(f"found {len(channels)} channels")

    # iterate through each found channel and convert it to a csv file
    pbar = tqdm(channels, desc="converting channels")
    for channel in channels:
        logging.info(f"converting channel {channel.name}")
        _channel_out = output_dir / f"{channel.name}.csv"
        subprocess.run(
            [
                "python3",
                "slack_json_to_csv.py",
                str(channel),
                str(users_path),
                _channel_out,
            ],
            check=True,
        )
        pbar.update(1)
    pbar.close()

    # aggregate all csv files in the output directory into a single csv file
    aggregate_CSVs(csv_dir=output_dir, output_loc=output_dir, output_file_type=merged_type)
