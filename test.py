
import os
import requests
import time
from lxml.html import fromstring
import justext
import readability
import trafilatura
import boilerpy3
import goose3
import html_text
import html2text
import newspaper
import sumy
import re



url = "https://www.oncrawl.com/technical-seo/extract-relevant-text-content-from-html-page/"

time_start = time.time()
# make it so that it doesn't say forbidden
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
html_string = response.text
time_end = time.time()
requests_time = time_end - time_start

time_start = time.time()
lxml_text = ''
try:
    lxml_text = fromstring(html_string, url).text_content()
except Exception as e:
    lxml_text = 'Error'
time_end = time.time()
lxml_time = time_end - time_start

time_start = time.time()
justext_text = ''
try:
    paragraphs = justext.justext(html_string, justext.get_stoplist("English"))
    for paragraph in paragraphs:
        justext_text += paragraph.text
except Exception as e:
    justext_text = 'Error'
time_end = time.time()
justext_time = time_end - time_start

time_start = time.time()
readability_text = ''
try:
    doc = readability.Document(html_string)
    readability_text = doc.summary()
except Exception as e:
    readability_text = 'Error'
time_end = time.time()
readability_time = time_end - time_start

time_start = time.time()
trafilatura_text = ''
try:
    trafilatura_text = trafilatura.extract(html_string)
except Exception as e:
    trafilatura_text = 'Error'
time_end = time.time()
trafilatura_time = time_end - time_start

time_start = time.time()
boilerpy3_text = ''
try:
    extractor = boilerpy3.extractors.ArticleExtractor()
    boilerpy3_text = extractor.get_content(html_string)
except Exception as e:
    boilerpy3_text = 'Error'
time_end = time.time()
boilerpy3_time = time_end - time_start

time_start = time.time()
goose3_text = ''
try:
    extractor = goose3.Goose()
    article = extractor.extract(raw_html=html_string)
    goose3_text = article.cleaned_text
except Exception as e:
    goose3_text = 'Error'
time_end = time.time()
goose3_time = time_end - time_start

time_start = time.time()
html_text_text = ''
try:
    extractor = html_text.HTMLText()
    html_text_text = extractor.handle(html_string)
except Exception as e:
    html_text_text = 'Error'
time_end = time.time()
html_text_time = time_end - time_start

time_start = time.time()
html2text_text = ''
try:
    extractor = html2text.HTML2Text()
    html2text_text = extractor.handle(html_string)
    match = re.search('<title>(.*?)</title>', html_string, re.IGNORECASE)
    title = match.group(1) if match else 'No title found'
    print(title)

except Exception as e:
    html2text_text = 'Error'
time_end = time.time()
html2text_time = time_end - time_start

time_start = time.time()
newspaper_text = ''
try:
    article = newspaper.Article(url)
    article.download()
    article.parse()
    newspaper_text = article.text
except Exception as e:
    newspaper_text = 'Error'
time_end = time.time()
newspaper_time = time_end - time_start

time_start = time.time()
sumy_text = ''
try:
    extractor = sumy.parsers.html.HtmlParser.from_url(url)
    sumy_text = extractor.document.text
except Exception as e:
    sumy_text = 'Error'
time_end = time.time()
sumy_time = time_end - time_start


    


print('html_string', len(html_string), requests_time)
print('lxml_text', len(lxml_text), lxml_time)
print('justext_text', len(justext_text), justext_time)
print('readability_text', len(readability_text), readability_time)
print('trafilatura_text', len(trafilatura_text), trafilatura_time)
print('boilerpy3_text', len(boilerpy3_text), boilerpy3_time)
print('goose3_text', len(goose3_text), goose3_time)
print('html_text_text', len(html_text_text), html_text_time)
print('html2text_text', len(html2text_text), html2text_time)
print('newspaper_text', len(newspaper_text), newspaper_time)
print('sumy_text', len(sumy_text), sumy_time)


timestamp = time.time()
os.mkdir(f'speed_test/{timestamp}')
# create a file for each of the above
with open(f'speed_test/{timestamp}/html_string.txt', 'w') as f:
    f.write(html_string)
f.close()
with open(f'speed_test/{timestamp}/lxml_text.txt', 'w') as f:
    f.write(lxml_text)
f.close()
with open(f'speed_test/{timestamp}/justext_text.txt', 'w') as f:
    f.write(justext_text)
f.close()
with open(f'speed_test/{timestamp}/readability_text.txt', 'w') as f:
    f.write(readability_text)
f.close()
with open(f'speed_test/{timestamp}/trafilatura_text.txt', 'w') as f:
    f.write(trafilatura_text)
f.close()
with open(f'speed_test/{timestamp}/boilerpy3_text.txt', 'w') as f:
    f.write(boilerpy3_text)
f.close()
with open(f'speed_test/{timestamp}/goose3_text.txt', 'w') as f:
    f.write(goose3_text)
f.close()
with open(f'speed_test/{timestamp}/html_text_text.txt', 'w') as f:
    f.write(html_text_text)
f.close()
with open(f'speed_test/{timestamp}/html2text_text.txt', 'w') as f:
    f.write(html2text_text)
f.close()
with open(f'speed_test/{timestamp}/newspaper_text.txt', 'w') as f:
    f.write(newspaper_text)
f.close()
with open(f'speed_test/{timestamp}/sumy_text.txt', 'w') as f:
    f.write(sumy_text)
f.close()



