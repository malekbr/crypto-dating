#!/usr/bin/env bash

python $(readlink -e server.py) > test_server_output.log 2> test_server_error.log &
echo "Server started at PID:" $server_pid
python test.py
pkill "python $(readlink -e server.py)"
