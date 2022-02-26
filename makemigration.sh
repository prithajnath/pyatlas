#!/usr/bin/env bash

echo "Type migration message: "
read commit

alembic revision -m "$commit"
