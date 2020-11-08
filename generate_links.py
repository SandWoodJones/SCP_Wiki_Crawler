#!/usr/bin/env python3

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from url_normalize import url_normalize
from progress_bar import print_progress_bar
import requests
from urllib.request import urlopen
import urllib.error
from curses import wrapper
import re
import yaml

re.MULTILINE = True

initialWebsite = "http://www.scpwiki.com/"

visited_links = set()
target_links_buffer = { initialWebsite }

blacklist = re.compile(r'^\/(system|forum|random|young-and-under-30)[/:]') # disables forum, system pages and newly posted articles

def save_to_yaml():
	with open("found_links.yaml", 'w+') as file:
		# write out found links to '.yaml' file in the correct format
		yaml.dump(list(visited_links), file, explicit_start=True, default_flow_style=False)

def main(stdscr):
	rows, _ = stdscr.getmaxyx()
	history_size = rows - 5
	site_history = ['' for _ in range(history_size)]

	while len(target_links_buffer) != 0:
		target = target_links_buffer.pop()

		try: # error catching
			response_object = urlopen(target) # turn url string into request
			soup = BeautifulSoup(response_object.read(), "html.parser") # turn request into soup
			add_to_history(site_history, target)
			visited_links.add(target)

			for link in get_soups_links(target, soup):
				if link not in visited_links: # if link is new
					target_links_buffer.add(link)

			print_progress_bar(stdscr, len(visited_links), len(target_links_buffer), bar_info(target, site_history))

		except urllib.error.HTTPError as e:
			print_progress_bar(stdscr, 1, 1, bar_info(target, site_history, True, e))
			continue
		except urllib.error.URLError as e:
			print_progress_bar(stdscr, 1, 1, bar_info(target, site_history, True, e))
			continue
		except KeyboardInterrupt: # so i can quit the program with ctrl+c
			raise
		except:
			print_progress_bar(stdscr, 1, 1, bar_info(target, site_history, True, "Unknown Error"))
			continue

	save_to_yaml()

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

def add_to_history(history, new_entry): # starts at the bottom and then goes up, moving everything backwards
	for i in range(len(history)):
		if i != 0:
			history.insert(i-1, history.pop(i))
	history[len(history) - 1] = new_entry

def bar_info(cur_site, history, fail=False, error=None):
	if fail:
		bar_info = f"{len(visited_links)} out of {len(target_links_buffer)}\nCurrently at {cur_site} ... FAILED - {error}\n\n"
		return bar_info

	bar_info = f"{len(visited_links)} out of {len(target_links_buffer)}\nCurrently at {cur_site}\n\n"
	for i in range(len(history)):
		bar_info += history[i] + '\n'
	return bar_info

wrapper(main)