#!/bin/bash
set -e

alembic upgrade head
exec python aiogram_run.py
