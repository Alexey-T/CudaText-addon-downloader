import sys
import os
import tempfile
import re
import json
import requests
import zipfile
import time
from urllib.parse import unquote

ch_def = [
  'https://raw.githubusercontent.com/Alexey-T/CudaText-registry/master/json/plugins.json',
  'https://raw.githubusercontent.com/Alexey-T/CudaText-registry/master/json/linters.json',
  'https://raw.githubusercontent.com/Alexey-T/CudaText-registry/master/json/data.json',
  'https://raw.githubusercontent.com/Alexey-T/CudaText-registry/master/json/snippets.json',
  'https://raw.githubusercontent.com/Alexey-T/CudaText-registry/master/json/lexers.json',
  'https://raw.githubusercontent.com/kvichans/CudaText-registry/master/kv-addons.json',
  ]

def get_remote_addons_list(channels):
    res = []
    print('Read channels:')
    for ch in channels:
        items = get_channel(ch)
        if items:
            res += items
        else:
            return
    return res

def get_channel(url):
    cap = url.split('/')[-1]

    #separate temp fn for each channel
    temp_dir = os.path.join(tempfile.gettempdir(), 'cudatext_addon_man')
    if not os.path.isdir(temp_dir):
        os.mkdir(temp_dir)
    temp_fn = os.path.join(temp_dir, cap)

    print('  getting:', cap)
    get_url(url, temp_fn, True)
    if not os.path.isfile(temp_fn): return

    text = open(temp_fn, encoding='utf8').read()
    d = json.loads(text)

    RE = r'http.+/(\w+)\.(.+?)\.zip'
    for item in d:
        parse = re.findall(RE, item['url'])
        item['kind'] = parse[0][0]
        item['name'] = unquote(parse[0][1])
    return d


def get_url(url, fn, del_first=False):
    fn_temp = fn+'.download'
    if os.path.isfile(fn_temp):
        os.remove(fn_temp)
    if del_first and os.path.isfile(fn):
        os.remove(fn)

    while True:
        try:
            r = requests.get(url, proxies=None, stream=True)
            with open(fn_temp, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        #f.flush() commented by recommendation

            if os.path.isfile(fn_temp):
                if os.path.isfile(fn):
                    os.remove(fn)
                os.rename(fn_temp, fn)
            return

        except Exception as e:
            print('error:', str(e))
            time.sleep(2)


print('Downloading list...')
items = get_remote_addons_list(ch_def)
if not items:
    print('Cannot download')
    sys.exit(0)

print('Downloaded list, %d items'%len(items))

res = sorted([item['url'] for item in items])
'''
with open('addons_links.txt', 'w') as f:
    for s in res:
        f.write(s+'\n')
'''

dir1 = 'addons'
if not os.path.isdir(dir1):
    os.mkdir(dir1)

for (i, url) in enumerate(res):

    kind = url.split('/')[-1].split('.')[0]
    fname = url.split('/')[-1]
    print('getting %d/%d: %s' % (i+1, len(res), fname))

    dir = os.path.join(dir1, kind)
    if not os.path.isdir(dir):
        os.mkdir(dir)
    fn_zip = os.path.join(dir, fname)

    get_url(url, fn_zip, True)
