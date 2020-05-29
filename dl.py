import os
import tempfile
import re
import json
import requests
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
        print('Cannot download:\n%s\n%s' % (url, str(e)))


print('Downloading list...')
items = get_remote_addons_list(ch_def)
if items:
    print('Downloaded')
    res = sorted([item['url'] for item in items])
    with open('addons_links.txt', 'w') as f:
        for s in res:
            f.write(s+'\n')
else:
    print('Cannot download')
