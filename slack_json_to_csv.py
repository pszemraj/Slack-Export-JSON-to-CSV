"""
slack_json_to_csv.py - given a directory of slack json files, converts them to a csv file. is executable.
"""
import json, sys
import os, csv
import re
from datetime import datetime
from cleantext import clean
from tqdm.auto import tqdm
import pandas as pd
from os.path import basename


def remove_string_extras(mytext: str):
    """
    remove_string_extras - removes extra characters from a string. everything except A-Za-z0-9 .,;
    """
    return re.sub(r"[^A-Za-z0-9 .,;]+", "", mytext)


def corr(s):
    """
    corr - adds space after period if there isn't one and adds spaces if needed
    """
    return re.sub(r"\.(?! )", ". ", re.sub(r" +", " ", s))


def handle_annotated_mention(matchobj):
    """
    handle_annotated_mention - handles the case where a mention is annotated with a user id
    """
    global user
    if isinstance(matchobj, list):
        matchobj = "".join(matchobj)
    return "@{}".format((matchobj.group(0)[2:-1]).split("|")[1])


def handle_mention(matchobj):
    """
    handle_mention - handles the general case where a mention is not annotated with a user id
    """
    global user
    if isinstance(matchobj, list):
        matchobj = "".join(matchobj)
    matched_user = remove_string_extras(matchobj.group(0))
    return "@{}".format(matched_user)


def transform_text(text: str):
    """
    transform_text - transforms the text of a message into a more readable format
    """
    text = text.replace("<!channel>", "@channel")
    text = text.replace("&gt;", ">")
    text = text.replace("&amp;", "&")
    # Handle "<@U0BM1CGQY|the100rabh> has joined the channel"
    text = re.compile("<@U\w+\|[A-Za-z0-9.-_]+>").sub(handle_annotated_mention, text)
    text = re.compile("<@U\w+>").sub(handle_mention, text)
    return text


if __name__ == "__main__":
    jsondir = sys.argv[1]
    userjson = sys.argv[2]
    outcsv_file = sys.argv[3]
    if len(sys.argv) > 4:
        verbose = sys.argv[4] == "verbose" or sys.argv[4] == "v"
    else:
        verbose = False

    content_list = []
    userlist = []
    f = open(outcsv_file, "w", encoding="utf-8", errors="ignore")
    user = {}
    with open(userjson, "r", errors="replace") as user_data:
        userlist = json.load(user_data)
        try:
            for userdata in userlist:
                userid = userdata["id"]
                if "real_name" in userdata and userdata["real_name"]:
                    realname = clean(userdata["real_name"])
                    if not re.match(".*[a-zA-Z].*", realname):
                        realname = clean(userdata["name"])
                else:
                    realname = clean(userdata["name"])
                if verbose:
                    print(f"realname for user {userid} is {realname}")
                user[userid] = [realname]
        except KeyError as e:
            print(f"KeyError: {e}\n\n User data: {userid}")
            sys.exit(1)

    if verbose:
        print("\n\tfinished loading user data\n")
    exclude_types = [
        "bot_message",
        "channel_join",
    ]  # types to exclude from the csv file (e.g. bot messages)
    csvwriter = csv.writer(
        f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\n"
    )
    csvwriter.writerow(["ts", "user", "text", "channel"])
    pbar = tqdm(total=len(os.listdir(jsondir)), desc="Processing files")
    for filename in os.listdir(jsondir):
        if filename.endswith(".json"):
            with open(
                os.path.join(jsondir, filename), "r", errors="replace"
            ) as json_data:
                data = json.load(json_data)
                for item in data:

                    if "subtype" in item.keys() and any(
                        item["subtype"] == x for x in exclude_types
                    ):
                        continue
                    if "user_profile" in item.keys():
                        _user_prof = item["user_profile"]
                        if "real_name" in _user_prof.keys():
                            user = clean(_user_prof["real_name"])
                        else:
                            user = clean(_user_prof["name"])
                    else:
                        # do the weird lookup they normally do
                        _user_cur = (
                            user[item["user"]] if item["user"] in user else ["unknown"]
                        )
                        user = clean(_user_cur[0])
                    ts = datetime.utcfromtimestamp(float(item["ts"]))
                    time = clean(ts.strftime("%Y-%m-%d %H:%M:%S"))
                    text = clean(transform_text(item["text"]))
                    channel = (
                        clean(item["channel"])
                        if "channel" in item.keys()
                        else basename(jsondir)
                    )
                    csvwriter.writerow([time, user, text, channel])
        pbar.update(1)
    pbar.close()

    if verbose:

        df = pd.read_csv(outcsv_file, quoting=csv.QUOTE_MINIMAL)
        print(f"A preview of the generated dataframe is:\n{df.head()}")

    f.close()
