# -*- coding: utf-8 -*-

from . import google_scraper
from . import malware_check
from . import alexa_rank
import tldextract


class MainApp:

    def __init__(self, kw, friends, competitors):
        self.kw = kw
        self.friends = friends
        self.competitors = competitors
        self.all_items = []

    def startapp(self):
        urls = []
        start = google_scraper.GoogleSearch(kw=self.kw, competitors=self.competitors,
                                            friends=self.friends)
        start.start()
        start.crawlpages(start.rankings)

        for x in start.rankings:
            linkul = tldextract.extract(x['url'])
            if linkul.subdomain != '':
                tld = linkul.subdomain + "." + linkul.domain + "." + linkul.suffix
            else:
                tld = linkul.domain + "." + linkul.suffix
            if tld not in urls:
                urls.append(tld)
            listaobiecte = dict()
            listaobiecte['domain'] = tld
            listaobiecte['url'] = x['url']
            listaobiecte['ranking'] = x['rank_no']
            listaobiecte['keyword'] = x['keyword']
            listaobiecte['search_traffic'] = ''
            listaobiecte['ranked_country'] = ''
            listaobiecte['friends_backlinks'] = x['friends_backlinks']
            listaobiecte['backlinks_competitor'] = x['backlinks_competitor']
            listaobiecte['external_links'] = x['external_links']
            listaobiecte['country_rank'] = ''
            listaobiecte['alexa_rank'] = ''
            listaobiecte['malware_status'] = 'Clean'
            listaobiecte['pageinfourls'] = []
            self.all_items.append(listaobiecte)

        alexalinks = ''
        for y in urls:
            alexalinks += y + "\r\n"

        alexarank = alexa_rank.AlexaRank(alexalinks)
        alexarank.getrank()

        for x in alexarank.linkuri:
            for z in self.all_items:
                if x['url'] == z['domain']:
                    z['alexa_rank'] = int(x['global'])
                    z['country_rank'] = int(x['countryrank'])
                    z['ranked_country'] = x['country']

        for x in start.pageinfo:
            for y in self.all_items:
                if x['url'] == y['url']:
                    y['pageinfourls'].append(x)

        mwchk = malware_check.MalwareCheck(start.rankings)
        for x in self.all_items:
            if x['url'] in mwchk.malwarelist:
                x['malware_status'] = 'Malware'

        return self.all_items

    def manualsearch(self, items):
        for x in items:
            linkul = tldextract.extract(x)
            if linkul.subdomain != '':
                tld = linkul.subdomain + "." + linkul.domain + "." + linkul.suffix
            else:
                tld = linkul.domain + "." + linkul.suffix
            listaobiecte = dict()
            listaobiecte['domain'] = tld
            listaobiecte['url'] = x
            listaobiecte['search_traffic'] = ''
            listaobiecte['ranked_country'] = ''
            listaobiecte['friends_backlinks'] = 0
            listaobiecte['backlinks_competitor'] = 0
            listaobiecte['external_links'] = 0
            listaobiecte['country_rank'] = ''
            listaobiecte['alexa_rank'] = ''
            listaobiecte['malware_status'] = 'Clean'
            listaobiecte['pageinfourls'] = []
            self.all_items.append(listaobiecte)

        start = google_scraper.GoogleSearch(kw=None, competitors=self.competitors,
                                            friends=self.friends)
        start.crawlpages(self.all_items)
        alexalinks = ''
        for y in self.all_items:
            alexalinks += y['domain'] + "\r\n"

        alexarank = alexa_rank.AlexaRank(alexalinks)
        alexarank.getrank()

        for x in alexarank.linkuri:
            for z in self.all_items:
                if x['url'] == z['domain']:
                    z['alexa_rank'] = x['global']
                    z['country_rank'] = x['countryrank']
                    z['ranked_country'] = x['country']

        for x in start.pageinfo:
            for y in self.all_items:
                if x['url'] == y['url']:
                    y['pageinfourls'].append(x)

        mwchk = malware_check.MalwareCheck(items)
        for x in self.all_items:
            if x['url'] in mwchk.malwarelist:
                x['malware_status'] = 'Malware'

        return self.all_items

    def resetitems(self):
        self.all_items = list()
