import os
import requests
import multiprocessing
from subprocess import check_output, CalledProcessError
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import codecs
import random

def returnsSameSSLCertHTTPConnect(url, proxy):
    try:
        with open(os.devnull, 'w') as devnull:
            unproxied = check_output("openssl s_client -showcerts -connect " + url + ":443 < /dev/null", shell=True, stderr=devnull)
            proxied = check_output("./openssl s_client -showcerts -proxy " + proxy + " -connect " + url + ":443 < /dev/null", shell=True, stderr=devnull)
        if ("failed" in proxied.lower() or "error" in proxied.lower()) and "CERTIFICATE" not in proxied:
            print "f"
            return False, "Proxy did not work-string matching"
        # Splitting because it includes a time and we only want to check the certs
        if unproxied.split("END CERT")[:-1] != proxied.split("END CERT")[:-1]:
            print "d"
            return proxied, "Proxy worked-Content mismatch"
        #if unproxied.split("END CERT")[:-1] == proxied.split("END CERT")[:-1]:
        else:
            print "g"
            return False, "Proxy worked-Content match"
    except CalledProcessError:
        pass
    print "e"
    return False, "Proxy did not work-exception"

def returnsSameSSLCertSocks(url, proxy):
    try:
        with open("proxychains.conf", "w") as f:
            config = """strict_chain\ntcp_read_time_out 15000\ntcp_connect_time_out 8000\n\n[ProxyList]\nsocks5 """ + proxy.replace(":", " ")
            f.write(config)
        with open(os.devnull, 'w') as devnull:
            unproxied = check_output("openssl s_client -showcerts -connect " + url + ":443 < /dev/null", shell=True, stderr=devnull)
            proxied = check_output("proxychains ./openssl s_client -showcerts -connect " + url + ":443 < /dev/null", shell=True, stderr=devnull)
        if ("failed" in proxied.lower() or "error" in proxied.lower()) and "CERTIFICATE" not in proxied:
            print "F"
            return False, "Proxy did not work-string matching"
        # Splitting because it includes a time and we only want to check the certs
        if unproxied.split("END CERT")[:-1] != proxied.split("END CERT")[:-1]:
            print "D"
            return proxied, "Proxy worked-Content mismatch"
        #if unproxied.split("END CERT")[:-1] == proxied.split("END CERT")[:-1]:
        else:
            print "G"
            return False, "Proxy worked-Content match"
    except CalledProcessError:
        pass
    print "E"
    return False, "Proxy did not work-exception"

def processProxy(*proxy):
    proxy = ''.join(proxy)
    results = []
    print "P"
    urls = ['news.ycombinator.com', 'daviddworken.com']
    for url in urls:
        results.append({'result':returnsSameSSLCertHTTPConnect(url, proxy),
                        'url':url,
                        'proxy':proxy,
                        'method':'HTTP Connect'})
        results.append({'result':returnsSameSSLCertSocks(url, proxy),
                        'url':url,
                        'proxy':proxy,
                        'method':'SOCKS'})
    # Dirty hack
    f = codecs.open('output/'+str(random.randint(0, 10000000))+'signedSSLChecker.log', 'wb', 'utf-8')
    for result in results:
        if result['result'][0]:
            f.write("*"*20+'\n')
            f.write('URL: ' + result['url'] + '\n')
            f.write('PROXY: ' + result['proxy'] + '\n')
            f.write('METHOD: ' + result['method'] + '\n')
            f.write("+"*20+'\n')
            f.write(result['result'][0])
            f.write("-"*20+'\n')
        else:
            f.write("PASSED: " + result['proxy'] + " on " + result['url'] + ' with method ' + result['method'] + ' for reason ' + result['result'][1] + '\n')
    f.close()


def getProxies():
    with open('/root/proxies.txt') as f:
        return [x for x in f.read().splitlines() if x != ""]

GLOBALLOCK = multiprocessing.Lock()

proxies = getProxies()

pool = multiprocessing.Pool(processes=32)
results = pool.map(processProxy, proxies)
