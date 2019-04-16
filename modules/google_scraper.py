import requests
from requests_html import HTMLSession
import urllib3
from requests.exceptions import ConnectionError, MissingSchema, InvalidSchema, TooManyRedirects, ReadTimeout,\
    ProxyError, ContentDecodingError
from fake_useragent import UserAgent

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class GoogleSearch:
    def __init__(self, kw=None, competitors=None, friends=None, pages=2):
        self.r = ''
        self.ua = UserAgent()
        self.ranks = dict()
        self.session = HTMLSession()
        self.session.headers.update({"User-Agent": self.ua.random})
        self.kw = kw
        self.response = ''
        self.urls = []
        self.friends = friends
        self.competitors = competitors
        self.rankings = []
        self.pageinfo = list()
        self.hasdata = 0
        self.pages = pages

    def start(self):
        self.searchforresults()

    def getnewproxy(self):
        proxy = requests.get(
            'http://falcon.proxyrotator.com:51337/?apiKey=wTJ6eLQx4Vv3z8UtauYfoyrN5sXkAh&userAgent=true&get=true&country=US')
        fullproxy = proxy.json()
        fullsox = fullproxy['proxy']
        return fullsox

    def searchforresults(self):
        for xz in self.kw:
            for page in range(0, int(self.pages)):
                if page == 0:
                    self.r = self.session.get('https://www.google.com/search?q=' + xz, verify=False)
                    if self.r.status_code == 503:
                        try:
                            proxies = {"http": "http://" + self.getnewproxy() + "",
                                       "https": "https://" + self.getnewproxy() + ""}
                            self.r = self.session.get('https://www.google.com/search?q=' + xz, verify=False,
                                                      proxies=proxies, timeout=20)
                        except ProxyError:
                            proxies = {"http": "http://" + self.getnewproxy() + "",
                                       "https": "https://" + self.getnewproxy() + ""}
                            self.r = self.session.get('https://www.google.com/search?q=' + xz, verify=False,
                                                      proxies=proxies, timeout=20)
                        except ReadTimeout:
                            continue
                        except ConnectionError:
                            continue
                        except TooManyRedirects:
                            continue
                    self.response = self.r.html.find('.r')
                    for z in range(0, len(self.response)):
                        self.urls.append(self.response[z].links)
                else:
                    r = self.session.get('https://www.google.com/search?q=' + xz + '&start=' + str(page) + '0',
                                         verify=False)
                    if r.status_code == 503:
                        try:
                            proxies = {"http": "http://" + self.getnewproxy() + "",
                                       "https": "https://" + self.getnewproxy() + ""}
                            self.r = self.session.get(
                                'https://www.google.com/search?q=' + xz + '&start=' + str(page) + '0',
                                verify=False, proxies=proxies)
                        except ProxyError:
                            proxies = {"http": "http://" + self.getnewproxy() + "",
                                       "https": "https://" + self.getnewproxy() + ""}
                            self.r = self.session.get(
                                'https://www.google.com/search?q=' + xz + '&start=' + str(page) + '0',
                                verify=False, proxies=proxies)
                        except ReadTimeout:
                            continue
                        except ConnectionError:
                            continue
                        except TooManyRedirects:
                            continue
                    self.response = r.html.find('.r')
                    for z in range(0, len(self.response)):
                        self.urls.append(self.response[z].links)
                    self.urls = list(self.urls)
            for x in range(0, len(self.urls)):
                self.ranks = dict()
                self.ranks["keyword"] = xz
                self.ranks["rank_no"] = x + 1
                self.ranks["url"] = str(self.urls[x]).replace("'", "").replace("{", "").replace("}", "")
                self.ranks['friends_backlinks'] = 0
                self.ranks['backlinks_competitor'] = 0
                self.ranks['external_links'] = 0
                self.rankings.append(self.ranks)
            self.urls = []
        return self.rankings

    def crawlpages(self, item):
        for x in range(0, len(item)):
            url = item[x]['url']
            z = HTMLSession()
            try:
                r = z.get(url, verify=False, timeout=10)
            except ContentDecodingError:
                continue
            except InvalidSchema:
                try:
                    r = z.get(url, verify=False, timeout=10)
                except Exception:
                    continue
            except ReadTimeout:
                continue
            except ConnectionError:
                continue
            except TooManyRedirects:
                continue
            except MissingSchema:
                if not str(url).startswith('http://'):
                    url = "http://" + url
                    try:
                        r = z.get(url, verify=False, timeout=10)
                    except Exception as e:
                        print(e)
                        continue
            obiectul = dict()
            obiectul['url'] = url
            obiectul['competitors'] = []
            obiectul['friends'] = []
            item[x]['external_links'] = item[x]['external_links'] + r.text.count('<a href="http://')
            item[x]['external_links'] = item[x]['external_links'] + r.text.count('<a href="https://')
            item[x]['external_links'] = item[x]['external_links'] + r.text.count("<a href='http://")
            item[x]['external_links'] = item[x]['external_links'] + r.text.count("<a href='https://")
            for z in self.friends:
                if z in r.text:
                    friend = dict()
                    friend['keyword'] = z
                    friend['backlinks'] = r.text.count(z)
                    item[x]['friends_backlinks'] = item[x]['friends_backlinks'] + r.text.count(z)
                    obiectul['friends'].append(friend)
                    self.hasdata = 1
            for y in self.competitors:
                if y in r.text:
                    competitor = dict()
                    competitor['keyword_competitor'] = y
                    competitor['backlinks'] = r.text.count(y)
                    item[x]['backlinks_competitor'] = item[x]['backlinks_competitor'] + r.text.count(y)
                    obiectul['competitors'].append(competitor)
                    self.hasdata = 1
            if self.hasdata == 1:
                self.pageinfo.append(obiectul)
                self.hasdata = 0
        return self.pageinfo

