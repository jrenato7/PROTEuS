#!/usr/bin/env bash

export FLASK_APP=/home/jrenato/PycharmProjects/master_degree_web/proteus/proteus.py
export FLASK_DEBUG=True
export PYTHONPATH=$PYTHONPATH:/home/jrenato/PycharmProjects/master_degree_web/proteus/

export BASE_DIR=/home/jrenato/PycharmProjects/master_degree_web/proteus/
export UPLOAD_FOLDER=/home/jrenato/PycharmProjects/master_degree_web/proteus/upload/
export USER_PROCESS_FOLDER=/home/jrenato/PycharmProjects/master_degree_web/proteus/static/user_aligns/


export SECRET_KEY=8292829282928292829
export MAIL_PASSWORD=mysql_pass

export WEBDB=proeng
export WEBDBUSER=root
export WEBDBPASS=root

export FULLDB=protein_align
export FULLDBUSER=root
export FULLDBPASS=root

export HOSTDB=127.0.0.1
pip install --editable .

flask run --host=0.0.0.0


