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

help:
  @just --list
