#!/usr/bin/python
"""
Simple client for calling RxNorm RxNav REST API.

https://rxnav.nlm.nih.gov/RxNormAPIREST.html
"""

import json
import urllib.request, urllib.error, urllib.parse

class RxNormClient:
    BASE_URL = 'https://rxnav.nlm.nih.gov/REST'

    def __init__(self):
        # 2/3 RxCUI's in dataset are unique, so don't make cache too fancy yet.
        self._cache = {}

    def fetch_properties_by_rxcui(self, rxcui):
        endpoint = 'rxcui/%s/allProperties.json?prop=all' % rxcui
        url = '/'.join([RxNormClient.BASE_URL, endpoint])

        # Read from cache or query API.
        if self._cache.get(url):
            properties = self._cache[url]
        else:
            properties = json.loads(urllib.request.urlopen(url).read())
            self._cache.update({url: properties})

        return properties

    def fetch_name_by_rxcui(self, rxcui):
        properties = self.fetch_properties_by_rxcui(rxcui)
        concepts = properties['propConceptGroup']['propConcept']
        for concept in concepts:
            if concept['propName'] == 'RxNorm Name':
                return concept['propValue']

        return None
