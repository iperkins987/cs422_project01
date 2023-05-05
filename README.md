# About ChronoWave

## Description:
This is a timeseries data management system. It facilitates the uploading and downloading of timeseries data.
In addition to data management, it also computes metrics with forecasting data and testing data.

## Authors:
Isaac Perkins, Aleks Stevens, Cynthia Meneses Cervon, Geoffrey Brendel

## Course:
CS 422 Project 1

## Directory Structure:

### modules
modules contains the database manager, our internal data representations, and our metrics computation manager.

### static
static contains css and javascript files however we only need a css file.

### template
template contains all html files needed to display content in the browser.

### test_files
test_files contains various formats of testing datasets and forecast data.

### working
working is a temporary directory used to store intermediate files.

### documents
documents contains all project documents such as SRS, SDS, ect.

## Usage:
Each page has instructions on how to use the tools and there is a help page located at the bottom
of the navigation bar for further assistance.

## Dependencies and Setup:
A list of dependencies is in the file requirements.txt. Follow the steps under "Getting Started" to setup the project.

# Getting Started

## Installing the requirements:

Install the requirements on your machine with:

### Windows: `pip install -r requirements.txt`
### Mac or Linux: `pip3 install -r requirements.txt`

## How to Run:

To launch the site just run the following:

### Windows: `python main.py`
### Mac or Linux: `python3 main.py`

The url should be displayed in the terminal it should be http://127.0.0.1:5000