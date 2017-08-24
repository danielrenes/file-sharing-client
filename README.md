# file-sharing-client


Create a configuration file in the root directory named: config

You need to specify the following:
  - SERVER_IP: the IP address where the file-sharing-server is running
  - SHARE: the directories you want to share
  - EXCLUDE: the directories and/or files you want to exclude from sharing
  - DOWNLOAD: the destination folder for your downloads

### Example:

SERVER_IP=127.0.0.1

SHARE=/home/\<username\>/shared

EXCLUDE=/home/\<username\>/shared/excludedDirectory;/home/\<username\>/shared/excludedFile

DOWNLOAD=/home/\<username\>/Downloads
