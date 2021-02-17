import logging
import collections
import csv
import re
import pandas as pd

import bs4
import requests

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('wb')

RES_HEADERS = (
		'fn',
		'url'
)

ParseResult = collections.namedtuple(
	'ParseResult',
	(
		'fn',
		'url'
	)
)

class Parser:
	def __init__(self):
		self.session = requests.Session()
		self.session.headers = {
				'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
				'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
				'Cookie': 'SESS7733ff205792bf820be8110b184ea169=ht1kdv43smblke41msi8pl9eru; has_js=1'
		}
		self.result = []
		self.url = ''

	def load_page(self, i:int):
			url = 'https://db.chgk.info/people' if i == 0 else 'https://db.chgk.info/people?page=' + str(i)
			res = self.session.get(url=url)
			res.raise_for_status()
			return res.text


	def parse_page(self, text:str):
			soup = bs4.BeautifulSoup(text, 'lxml')
			container = soup.select('table.sticky-enabled > tbody > tr > td:nth-child(2) > a')
			for block in container:
					self.parse_block(block=block)

	def parse_block(self, block):
		url = 'https://db.chgk.info' + block.get('href')
		fn = block.text.strip()
		self.result.append(ParseResult(fn=fn, url=url))

	def save_results(self):
				path = '/Users/andreyp/Documents/repo/udav-projects/prsrchgk/authors.csv'
				with open(path, 'a') as f:
						writter = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
						# if i == 0:
						writter.writerow(RES_HEADERS)
						for item in self.result:
								writter.writerow(item)

	def run(self, i:int):
		text = self.load_page(i=i)
		self.parse_page(text=text)



QUESTION_HEADERS = (
		'question',
		'answer',
		'author'
)

QuestionParseResult = collections.namedtuple(
	'QuestionParseResult',
	(
		'question',
		'answer',
		'author'
	)
)

class SimpleQuestion:
	def __init__(self):
		self.session = requests.Session()
		self.session.headers = {
				'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
				'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
				'Cookie': 'SESS7733ff205792bf820be8110b184ea169=ht1kdv43smblke41msi8pl9eru; has_js=1'
		}
		self.result = []

	def load_page(self, url: str):
			res = self.session.get(url=url)
			res.raise_for_status()
			return res.text

	def parse_page(self, text:str):
			soup = bs4.BeautifulSoup(text, 'lxml')
			container = soup.select('dd > div.question')
			for block in container:
					self.parse_block(block=block)

	def get_text(self, block):
			text = block.text.split(': ', 1)[1].strip()
			return re.sub(r'\n', ' ', text)

	def parse_block(self, block):
		dirtyQuestion = block.select_one('p:first-of-type')
		question = self.get_text(dirtyQuestion)
		dirtyAnswer = block.select_one('p:nth-child(2)')
		answer = self.get_text(dirtyAnswer)
		self.result.append(QuestionParseResult(question=question, answer=answer, author=self.url))

	def save_results(self):
				path = '/Users/andreyp/Documents/repo/udav-projects/prsrchgk/questions1.csv'
				with open(path, 'a') as f:
						writter = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
						writter.writerow(QUESTION_HEADERS)
						for item in self.result:
								writter.writerow(item)

	def run(self, url:str):
		self.url = url
		text = self.load_page(url=url)
		self.parse_page(text=text)

# if __name__ == '__main__':
# 	parser = Parser()
#
# 	i = 0
# 	while i <= 157:
# 		parser.run(i=i)
# 		i += 1
#
# 	parser.save_results()

if __name__ == '__main__':
	i = 0
	question = SimpleQuestion()
	col_list = ['url']
	data_cols = pd.read_csv("/Users/andreyp/Documents/repo/udav-projects/prsrchgk/authors.csv", usecols=col_list)
	url_list = data_cols["url"]
	for url in url_list:
		logger.info(i)
		question.run(url=url)
		i+=1

	question.save_results()
	logger.info('DONE EBAT')
