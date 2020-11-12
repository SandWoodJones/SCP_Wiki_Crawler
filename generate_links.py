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

initialWebsite = "http://www.scpwiki.com/"

visited_links = set()
target_links_buffer = { initialWebsite }

 # skips the forum, system and author pages, newly posted and archived articles, etc
 # TODO: maybe move this to somewhere else. dont know where
blacklist = re.compile(
	r'('
		r'^\/('
			r'system|forum|random|news-\d{2}-\d{4}|'
			r'young-and-under-30|new-pages-feed|most-recently-(edited|created)|'
			r'(scp|tale)-calendar|top-rated-pages-by-month-\d{4}|'
			r'licensing-master-list|'
			r'miss-lohner-s-sandbox|bluesoul|/decibelle-s-workbench|'
			r'local--files'
		r')[/:]?|'
		r'.*('
			r'author-page|personnel-file|archive(-i+)*|#.*'
		r')$'
	r')'
)

def save_to_yaml(): # TODO: write this myself to get indentation how i want it
	with open("found_links.yaml", 'w+') as file:
		# write out found links to '.yaml' file in the correct format
		yaml.dump(list(visited_links), file, explicit_start=True, default_flow_style=False)

def main():

	while len(target_links_buffer) != 0:
		target = target_links_buffer.pop()

		# TODO: make this into its own function
		try: # error catching
			html_document = urlopen(target).read() # get .html from url
		except IncompleteRead as e:
			html_document = e.partial
		except ConnectionResetError: # TODO: implement retry here
			continue
		except urllib.error.HTTPError as e:
			continue
		except urllib.error.URLError as e:
			continue
		except:
			raise

		soup = BeautifulSoup(html_document, "html.parser") # turn .html into soup
		visited_links.add(target)

		for new_link in get_soups_links(target, soup):
			if new_link not in visited_links: # if link is new
				target_links_buffer.add(new_link)

		print(f"{target} || {len(visited_links)} out of {len(visited_links) + len(target_links_buffer)} ({len(target_links_buffer)} left)")

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

main()