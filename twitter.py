#!/usr/bin/env python

from pymongo import MongoClient
from mongoengine import connect
from mongoengine.context_managers import switch_collection
connect('test')

import requests
import hmac, hashlib
from random import randint
from base64 import b64encode
from urllib import quote as percent_encode
import time
import json
from db.tweet import Tweet


OAUTH_CONSUMER_KEY='YXETsoXQHwmAiTAEATs8wA'
OAUTH_CONSUMER_SECRET='EbShWrfFxfsCkLHCWp5DO64djbKLResDdm6pv5M9s'
ACCESS_TOKEN='2331234997-CqgYy3oQQHeQRMPn2vTnu6YMerxfsIcqY6FAT79'
ACCESS_TOKEN_SECRET='Sn9uQtW7mnLt3qlv7kZyuzSfZ0QgqcHw6mrCsR7z8s0ve'
OAUTH_SIG_METHOD='HMAC-SHA1'
OAUTH_VERSION='1.0'

TWITTER_SAMPLE_STREAM='https://stream.twitter.com/1.1/statuses/sample.json'

nonce = lambda: b64encode(''.join(str(randint(0,100)) for _ in range(32)))

mc = MongoClient()
db = mc.get_database('tweets')


def oauthd():
    return dict( oauth_version=OAUTH_VERSION
               , oauth_consumer_key=OAUTH_CONSUMER_KEY
               , oauth_token=ACCESS_TOKEN
               , oauth_signature_method=OAUTH_SIG_METHOD
               , oauth_nonce=nonce()[:32]
               , oauth_timestamp=int(time.time())
               )


def signature_base_string(method, url, **params):
    method = method.upper()
    url = percent_encode(url, safe='')
    plist = percent_encode('&'.join('%s=%s' % (k, params[k]) for k in sorted(params.keys())))
    return '&'.join([method, url, plist])


def signing_key():
    return '&'.join(percent_encode(x) for x in [OAUTH_CONSUMER_SECRET, ACCESS_TOKEN_SECRET])


def get_stream(delimited='length', filter_level='none', language='en'):
    sign_dict = oauthd()
    sign_string = signature_base_string('GET', TWITTER_SAMPLE_STREAM, delimited=delimited, filter_level=filter_level, language=language, **sign_dict)
    sign_key = signing_key()
    
    _hash = hmac.new(sign_key, sign_string, hashlib.sha1)
    oauth_signature = _hash.digest().encode('base64')
    sign_dict['oauth_signature'] = percent_encode(oauth_signature)
    
    headers={'Authorization': ('OAuth ' + ', '.join(('%s="%s"' % (k, sign_dict[k])) for k in sorted(sign_dict.keys())))}
    print json.dumps(headers,indent=1)
    return requests.get(TWITTER_SAMPLE_STREAM, params=dict(delimited=delimited, filter_level=filter_level, language=language), headers=headers, stream=True)


def stream_iterator(stream):
    last_tweet_ts = time.time()
    stiter = iter(stream)
    ct, t = '', None
    to_read, rest = 0, ''
    while True:
        if not t:
            t = stiter.next()

        t = t.split('\r\n')
        if all((not x or not x.strip()) for x in t):
            # newline keep-alive
            t = None
            continue

        t = t[:2]
        to_read, rest = t
        to_read = int(to_read.strip()) - 2

        while to_read > 0:
            ct += rest[:to_read]
            t = rest[to_read:]
            to_read -= len(rest)
            if to_read > 0:
                rest = stiter.next()

        now = time.time()
        time.sleep(2 - (now - last_tweet_ts)
                   if now - last_tweet_ts < 2
                   else 0)
        print ct
        last_tweet_ts = time.time()
        print 'db'
        db['stream'].insert(json.loads(ct))
        print 'Tweet'
        j = json.loads(ct)
        tweet = Tweet(**j)
        print 'save'
        print tweet.save()
        print 'yield'
        yield json.loads(ct)

        to_read, rest, ct = 0, '', ''


if __name__ == '__main__':
    stream = get_stream()
    print stream
    for t in stream_iterator(stream):
        print json.dumps(t, indent=1)
        break

    for o in Tweet.objects:
        print o.id


