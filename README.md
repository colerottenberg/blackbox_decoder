# BlackBox 

<!-- ! Add a badge for the workflow -->
![workflow](https://github.com/colerottenberg/blackbox_decoder/actions/workflows/tests.yml/badge.svg)

## Table of Contents
- [BlackBox](#blackbox)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Installation](#installation)
    - [Poetry](#poetry)
  - [Usage](#usage)

## Introduction

**BlackBox** is a tool that allows you to decode logs from the the ALED Powerboard. The tool is written in Python and uses the following libraries:
- [Pandas](https://pandas.pydata.org/)
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/intro)
- [Bitstring](https://pypi.org/project/bitstring/)
- [Matplotlib](https://matplotlib.org/)

The application works by reading the log file and decoding the data into a human readable format. The user can then view the data in multiple plots and graphs.

## Installation

To install the Log Decoder, you need to have Python 3 installed on your computer. Afterwards, clone the repository and install the required dependencies using the following commands:

```bash
git clone https://github.com/BlueVigil/LogDecoder.git
cd LogDecoder
```

### Poetry

The BlackBox application uses Poetry to manage its dependencies. To install the dependencies, run the following command:

```bash
poetry install
```

To run the application, use the following command:

```bash
poetry run python blackbox_decoder/app.py
```

## Usage

To use the application, the user needs to open the application and select the *Browse* button to select the log file. The user can then select the *Decode* button to decode the log file. A new window will open with the decoded data. Using the Navigation bar at the top, the user can select the data they want to view.

For testing purposes, the user can use the log file provided in the repository. The log file is located in the *logs* folder.
