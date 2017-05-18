import requests
import multiprocessing
import hashlib

def returnsSameContent(url, proxy):
    unproxied = requests.get(url)
    try:
        print "Tick on " + proxy
        proxied = requests.get(url, proxies={'http':'http://'+proxy, 'https':'https://'+proxy}, timeout=1)
        print "Proxy is up: HTTP! {}".format(proxy)
        if unproxied.text != proxied.text:
            return proxied.text
        return False
    except:
        try:
            proxied = requests.get(url, proxies={'http':'socks5://'+proxy}, timeout=1)
	    print "Proxy is up: SOCKS! {}".format(proxy)
            if unproxied.text != proxied.text:
                return proxied.text
            return False
        except:
            print "Proxy is down!"
            return False

def processProxy(proxy, urls=['http://dl.google.com/tag/s/appguid%3D%7B8A69D345-D564-463C-AFF1-A69D9E530F96%7D%26iid%3D%7BBF72A9ED-53C1-BC3D-C9E4-6D58F17DF260%7D%26lang%3Den%26browser%3D4%26usagestats%3D1%26appname%3DGoogle%2520Chrome%26needsadmin%3Dprefers%26ap%3Dx64-stable/update2/installers/ChromeSetup.exe']):
    results = []
    print "Progress!"
    for url in urls:
        results.append({'result':returnsSameContent(url, proxy),
                        'url':url,
                        'proxy':proxy})
    return results

def getProxies():
    with open('/root/proxies.txt') as f:
        return [x for x in f.read().splitlines() if x != ""]

proxies = getProxies()
logfile = 'exeManip.log'
import codecs
f = codecs.open(logfile, 'wb', 'utf-8')

pool = multiprocessing.Pool(processes=16)
results = pool.map(processProxy, proxies)
for proxyResults in results:
    for result in proxyResults:
        if result['result']:
            f.write("*"*20+'\n')
            f.write('URL: ' + result['url'] + '\n')
            f.write('PROXY: ' + result['proxy'] + '\n')
            f.write("+"*20+'\n')
            f.write(result['result'])
            f.write("-"*20+'\n')
        else:
            f.write("PASSED: " + result['proxy'] + " on " + result['url'] + '\n')

f.close()

