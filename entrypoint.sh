#!/usr/bin/env bash

alembic upgrade head
python app.py
