# Slack-Export-JSON-to-CSV

Convert Slack messages exported in their complicated JSON format to simple CSV format.

_this is a fork with upgraded functionality, i.e. it can handle multiple channels and users_

## usage

### converting one file

```shell
python slack_json_to_csv.py folder_of_channel_to_export path_to_slack_users.json path_to_output_slack_messages.csv

```

eg.

```shell
python slack_json_to_csv.py slack_export/channelA slack_export/users.json output.csv
```

### converting multiple files

-   first, unzip the exported file from slack, root folder that contains all channels in subfolders
-   then, run the following command

```shell
python convert_workspace.py -i PATH_TO_ROOT_FOLDER -o PATH_TO_OUTPUT_FOLDER -u PATH_TO_USERS_JSON -t FILE_TYPE_FOR_EXPORT
```

---
