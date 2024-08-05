# This is a justfile

default:
  @just --list

run:
  poetry run blackbox-decoder

install:
  poetry install

update:
  poetry update

test:
  poetry run python -m pytest

black:
  poetry run black blackbox_decoder
  poetry run black tests

flake:
  poetry run flake8 --max-line-length=88

help:
  @just --list
