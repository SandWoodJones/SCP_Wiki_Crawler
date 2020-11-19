#!/usr/bin/env python3

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from url_normalize import url_normalize
from http.client import IncompleteRead
from urllib.request import urlopen
import urllib.error
import re
import yaml

re.MULTILINE = True

with open("config.yaml", "r") as file:
	config = yaml.safe_load(file)

initialWebsite = config["initial_site"]

visited_links = set()
target_links_buffer = { initialWebsite }

# makes it easy to add more patterns in the config
def make_regex_pattern():
	pattern = r"("
	for i in range(len(config["blacklisting_regex"])):
		cur = config["blacklisting_regex"][i][2:-1]
		pattern += cur
		if i != len(config["blacklisting_regex"]) - 1:
			pattern += "|"
	pattern += ")"
	return pattern

blacklist = re.compile(make_regex_pattern())

def save_to_yaml(): # TODO: write this myself to get indentation how i want it
	with open("found_links.yaml", 'w+') as file:
		# write out found links to '.yaml' file in the correct format
		yaml.dump(list(visited_links), file, explicit_start=True, default_flow_style=False)

def main():
	while len(target_links_buffer) != 0:
		target = target_links_buffer.pop()

		html_document = get_html(target)
		if html_document == -1: continue # if link is broken skip to next

		soup = BeautifulSoup(html_document, "html.parser") # turn .html into soup
		visited_links.add(target)

		for new_link in get_soups_links(target, soup):
			if new_link not in visited_links: # if link is new
				target_links_buffer.add(new_link)

		draw_progress(target, len(visited_links) + len(target_links_buffer), len(visited_links))
		#print(f"{target} || {len(visited_links)} out of {len(visited_links) + len(target_links_buffer)} ({len(target_links_buffer)} left)")

	save_to_yaml()

# takes url string and correctly converts it into a .html file
def get_html(url, tries=0):
	if tries >= 3: return -1
	try:
		html_doc = urlopen(url).read()
	except IncompleteRead as e:
		html_doc = e.partial
	except ConnectionResetError: # retries it 3 times before giving up
		get_html(url, tries+1)
	except (urllib.error.HTTPError, urllib.error.URLError):
		return -1
	except:
		raise

	return html_doc

def get_soups_links(soups_parent, targeted_soup):
	found_links = set()

	for link in targeted_soup.find_all('a'): # get all of the soup's links
		if link.get('href'): # if the link element is an url
			newLink = link.get('href')
			if newLink.startswith('/'): # if the url is an absolute one and doens't leave the parent website
				if not blacklist.search(newLink): # applies blacklist matching
					newLink = urljoin(soups_parent, newLink) # makes the url into an absolute url if necessary
					found_links.add(url_normalize(newLink))
	return found_links

def draw_progress(current_link, total_n, current_n):
	pass

main()