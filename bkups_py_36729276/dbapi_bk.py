# -*- coding: utf-8 -*-

# Author: 1dragosh

from pymongo import MongoClient
from bson.objectid import ObjectId


class dbapius:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.us_seo
        self.items = self.db.items
        self.user = self.db.user_settings
        self.site = self.db.site_settings
        self.kwgroup = self.db.kw_groups
        self.history = self.db.history_reports
        self.stats = self.db.stats_info

    '''
    Username Settings
    '''

    def getusername(self):
        username = self.user.find_one({"username": {'$exists': 1}})['username']
        password = self.user.find_one({"password": {'$exists': 1}})['password']
        return username, password

    def getfriends(self):
        friends = self.user.find_one({"username": {'$exists': 1}})['friends']
        return friends

    def getcompetitors(self):
        competitors = self.user.find_one({"username": {'$exists': 1}})['competitors']
        return competitors

    '''
    Filter Settings
    '''

    def alexarankfilter(self):
        ranksettings = self.site.find_one({"alexa_filter_rank": {'$exists': 1}})['alexa_filter_rank']
        return int(ranksettings)

    '''
    Database operations
    '''

    def readkwgroup(self):
        names = self.kwgroup.find({})
        groups = []
        for x in names:
            groups.append(x['name'])
        return groups

    def getkwfromgroup(self, group_name):
        kws = self.kwgroup.find_one({"name": group_name})['keywords']
        return kws

    def addkwandgroup(self, item):
        self.kwgroup.insert_one(item)

    def deletekwgroup(self, group_name):
        group = self.kwgroup.remove({"name": group_name})
        return group

    def addtohistory(self, item):
        self.history.insert_one(item)

    def readhistory(self):
        cursor = self.history.find({})
        history = list()
        for document in cursor:
            history.append(document)
        return history

    def additemsalone(self, item):
        self.items.insert_one(item)

    def readhistoryreport(self, theid):
        document = self.history.find_one({"_id": ObjectId(theid)})
        return document

    def deletereport(self, theid):
        self.history.remove({"_id": ObjectId(theid)})

    def clearitems(self):
        self.items.remove({})

    def getallitems(self):
        cursor = self.items.find({})
        lista = list()
        for document in cursor:
            lista.append(document)
        return lista

    def getcolors(self):
        colors = self.site.find_one({"alexa200": {'$exists': 1}})
        return [colors['alexa200'], colors['alexa400'], colors['alexa600'], colors['alexa800'], colors['alexa1000']]

    def getoneitem(self, theid):
        document = self.items.find_one({"_id": ObjectId(theid)})
        return document

    def getonehistoryitem(self, theid):
        document = self.history.find_one({"_id": ObjectId(theid)})
        return document

    def getstats(self):
        currkw = self.stats.find_one({"kw_groups": {'$exists': 1}})['kw_groups']
        history = self.stats.find_one({"history_reports": {'$exists': 1}})['history_reports']
        self.stats.find_one_and_update({"kw_groups": currkw},
                                       {"$set": {"kw_groups": len(self.readkwgroup())}})
        self.stats.find_one_and_update({"history_reports": history},
                                       {"$set": {"history_reports": self.history.count()}})
        stats = self.stats.find_one({"kw_groups": {'$exists': 1}})
        return stats

    def updatecrawls(self):
        crawls = self.stats.find_one({"crawls": {'$exists': 1}})['crawls']
        self.stats.find_one_and_update({"crawls": crawls},
                                       {"$set": {"crawls": (crawls + 1)}})

    def updatepurls(self, len):
        parsed_urls = self.stats.find_one({"parsed_urls": {'$exists': 1}})['parsed_urls']
        self.stats.find_one_and_update({"parsed_urls": parsed_urls},
                                       {"$set": {"parsed_urls": (parsed_urls + len)}})

    def updatelogin(self, newdate, newip):
        old_login_ip = self.stats.find_one({"last_login_ip": {'$exists': 1}})['last_login_ip']
        old_login_date = self.stats.find_one({"last_login_date": {'$exists': 1}})['last_login_date']
        self.stats.find_one_and_update({"last_login_ip": old_login_ip},
                                       {"$set": {"last_login_ip": newip}})
        self.stats.find_one_and_update({"last_login_date": old_login_date},
                                       {"$set": {"last_login_date": newdate}})
