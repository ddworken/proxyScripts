import requests
import multiprocessing

def returnsSameContent(url, proxy):
    unproxied = requests.get(url)
    try:
        print "Tick on " + proxy
        proxied = requests.get(url, proxies={'http':'http://'+proxy, 'https':'https://'+proxy}, timeout=5)
        print "Proxy is up: HTTP! {}".format(proxy)
        if unproxied.text != proxied.text:
            return proxied.text
        return False
    except:
        try:
            proxied = requests.get(url, proxies={'http':'socks5://'+proxy}, timeout=5)
	    print "Proxy is up: SOCKS! {}".format(proxy)
            if unproxied.text != proxied.text:
                return proxied.text
            return False
        except:
            print "Proxy is down!"
            return False

def processProxy(proxy, urls=['http://example.com', 'http://code.jquery.com/jquery-3.2.1.js', 'http://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css']):
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
urls = ['http://example.com', 'http://code.jquery.com/jquery-3.2.1.js', 'http://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css']
logfile = 'htmlManip.log'
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

