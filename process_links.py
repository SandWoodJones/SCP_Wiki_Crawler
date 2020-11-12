#!/usr/bin/env python3

import yaml
from shutil import copyfile
from os.path import isfile

with open("config.yaml", "r") as file:
	config = yaml.safe_load(file)

if not isfile(config["links_file"] + ".sav"):
	copyfile(config["links_file"], config["links_file"] + ".sav")

list_of_links = []
with open(config["links_file"], 'r') as f:
	fc = yaml.safe_load(f)
	list_of_links = fc

list_of_links.sort()

# with open(config["links_file"], "w+") as f:
# 	yaml.dump(list_of_links, f, explicit_start=True, default_flow_style=False)