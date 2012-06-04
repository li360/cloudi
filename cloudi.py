#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import sys
import os
from cache import Cache
import platform
from HTMLParser import HTMLParser
import json
from color import lgreen, dgreen, white, lgreen_s, ed, red


def get_clip():
    pf = platform.system().upper()
    if pf.startswith('LINUX'):
        clip = os.popen('xsel').read()
    elif pf.startswith('CYGWIN'):
        with open('/dev/clipboard') as clipboard:
            clip = clipboard.read()
    elif pf.startswith('WINDOWS'):
        # Windows...
        import win32clipboard
        win32clipboard.OpenClipboard()
        clip = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
    return clip


def invoke_api(base_url, word):
    url = base_url + urllib2.quote(word)
    try:
        return urllib2.urlopen(url).read()
    except IOError:
        print 'Please Check your network connection.'
        exit()


def parse(word, json_str):
    json_dict = json.loads(json_str)
    err = json_dict.get('err', None)
    if err:
        sugg_url = 'http://dict.qq.com/sug?'
        print invoke_api(sugg_url, word).strip().decode('gbk') or red(err)
    else:
        print_result(json_dict)
        Cache.cache_word(word, json_str)


def print_result(dct):
    local = dct.get('local', None)
    if local and local[0]:
        local = local[0]
    else:
        print red('Sorry no result.')
        exit()
    prons = (''.join([p + ', ' for p in local.get('pho', [])]))[:-2]
    word = local.get('word', None)
    similar = u'同义词:\n'
    for s in local.get('syn', []):
        similar += s['p'] + '\n'
        for w in s['c']:
            similar += '  ' + w
    mor = ''.join(['%s: %s ' % (d['c'], lgreen(d['m'])) for d in local.get('mor', [])])
    des = ''
    for d in local.get('des', []):
        if dct['lang'] == 'ch':
            des += d
        else:
            des += d.get('p', '') + '\n'
            des += white(d.get('d', ''))
        des += '\n'
    sents = ''
    for sent in local.get('sen', []):
        s_type = sent['p']
        sents += s_type + '\n'
        for s in sent['s']:
            sents += '  %s\n' % s['es'].replace('<b>', lgreen_s).replace('</b>', ed)
            sents += '  %s\n' % dgreen(s['cs'])

    result = ''
    result += '\n%s [%s]\n' % (lgreen(word), dgreen(prons or 'no soundmark'))
    if mor:
        result += '\n%s\n' % mor
    result += '\n' + des
    result += '\n' + sents
    if len(similar) > 5:
        result += '\n' + similar + '\n'

    print HTMLParser.unescape.__func__(HTMLParser, result)


if __name__ == '__main__':
    query_url = 'http://dict.qq.com/dict?q='
    if len(sys.argv) > 1:
        word = (''.join([w + ' ' for w in sys.argv[1:]])).strip()
    else:
        word = get_clip()
    json_str = Cache.get_exp(word)
    if not json_str:
        json_str = invoke_api(query_url, word)
    parse(word, json_str)