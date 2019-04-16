from urllib.parse import urlencode
from requests_html import HTMLSession


class AlexaRank:
    def __init__(self, urls):
        self.r = HTMLSession()
        self.r.headers.update({'Referer': 'https://massalexa.com/'})
        self.r.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
        self.r.headers.update({'Host': 'massalexa.com'})
        data = dict()
        data['massurladdress'] = urls
        self.query = urlencode(data, doseq=True)
        self.linkuri = list()

    def getrank(self):
        z = self.r.post('https://massalexa.com/', self.query, verify=False)
        response = z.html.find('tr')
        for z in range(1, len(response)):
            raspuns = response[z].text.split('\n')
            ranking = dict()
            try:
                ranking['url'] = raspuns[0]
            except IndexError:
                continue
            try:
                ranking['global'] = raspuns[1]
            except IndexError:
                continue
            try:
                ranking['country'] = raspuns[2]
            except IndexError:
                continue
            try:
                ranking['countryrank'] = raspuns[3]
            except IndexError:
                continue
            self.linkuri.append(ranking)
