#!/bin/bash
redis-server --daemonize yes
flask --app api run --host=0.0.0.0
