# TTN Coverage

This script parses node data from [The Things Network API](http://thethingsnetwork.org/api/v0/nodes/) and creates GeoJSON files of the effective network coverage.

### Installation

Make sure you have Python 3 installed, clone this repository and create a `virtualenv` to install dependencies:

    $ virtualenv -p python3 .env
    $ source .env/bin/activate
    $ pip install -r requirements.txt

### Usage

Run the import for your node:

    $ python import.py <node_eui>

For now, this only understands a very specific format of encoding coordinates in the `data_plain` field, but this will be improved soon.
