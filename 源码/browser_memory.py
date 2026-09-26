from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlsplit,unquote
ROOT=Path(__file__).resolve().parent.parent
def inline_html(path):
 soup=BeautifulSoup(path.read_text(),'html.parser')
 for link in soup.select('link[rel="stylesheet"]'):
  p=ROOT/unquote(urlsplit(link['href']).path)
  st=soup.new_tag('style');st.string=p.read_text();link.replace_with(st)
 for script in soup.select('script[src]'):
  p=ROOT/unquote(urlsplit(script['src']).path)
  del script['src'];script.string=p.read_text()
 return str(soup)
def load(page,name):
 page.set_content(inline_html(ROOT/name),wait_until='load')
 page.wait_for_timeout(60)
