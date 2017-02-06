#!/usr/bin/env bash

rm musictool.db
python3 cmd.py install
#python3 cmd.py add_library <lib_name> <your_path_to_lib>
#python3 cmd.py create_playlist test_playlist playlist_desc
#python3 cmd.py add_file_to_playlist 1 1
#python3 cmd.py remove_playlist 1
#python3 cmd.py play_file_server 1