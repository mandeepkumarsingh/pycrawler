'''
Created on 23-Nov-2017

@author: pankaj.katiyar
'''

import re
import traceback
import sys
# import requests
import threading
import http
import urllib3
import configparser

class SaareMethods():

    'contains information about damn pages'
    damnPagesMap = {}
    
    'this map will be used to keep all values'
    globalUrlMap = {}
        
    'this will keep unique urls which are already traversed - to avoid repetition'
    globalTraversedSet = set()
        
  
  
    def get_config_param(self, section, key):
        config = configparser.ConfigParser()
        config.read("/Users/pankaj.katiyar/Desktop/Automation/PythonCrawler/config/config.ini")
        self.config = config

        return self.config.get(section, key)
  
  
    ''' get domain from received url '''
    def ifLenskartDomain(self, url):
        url1 = url[url.find('//')+2:]
        url2 = url1[:url1.find('/')]
        
#         print('domain: '+url2 + ' from received url: '+url)
        
        if url2.find('lenskart') > -1:
            return True
        else:
            return False
        
        
    ''' launch crawler through executor using list '''
    def launchCrawlerUsingList(self):
#         while len(self.globalUrlList) > 0:   
        
        'global list will be updated dynamically by many threads '
        tempList = self.globalUrlList     
        
        print(' =======  iteration list is now  ==> ', len(tempList))
           
        for url in tempList:
            try:
                self.performTaskWithoutBrowser(url)
            except Exception:
                print('error ---> ')
            
    
    ''' launch crawler through executor using map '''
    def launchCrawlerUsingMap(self):
        
        url = ''
        for k,v in self.globalUrlMap.items():
            if(v==False):
                url = k
                                
                try:
                    lock = threading.RLock()
                    lock.acquire(blocking=True)
                     
                    ' remove url from global map '
#                     self.globalUrlMap.pop(k)
                    self.globalUrlMap.update({k:True})
 
                finally:
                    lock.release()
                                
                break
            
        if(url != ''):
            
            print()
            print("Task Executed {} by ", format(threading.current_thread()), 'global map now - ', len(self.globalUrlMap), ' and url is ==> '+url)
            self.performTaskWithoutBrowser(url)
        
        
    ''' perform task ==> get url, browse it and check it if its a DAMN and then find the url list and return this '''
    def performTaskWithoutBrowser(self, url):
        
        try:
            url = str(url)
 
            'check only those urls which starts with http and not traversed earlier and having lenskart domain'
            if(url in self.globalTraversedSet):
                pass
               
            elif not (self.ifLenskartDomain(url)):
                pass
                  
            elif not(url.startswith('http')):
                pass
                    
            else:
                try:
                    'keep a copy so that its not traversed again'
                    lock = threading.RLock()
                    lock.acquire(blocking=True)
                    try:
                        self.globalTraversedSet.add(url)
                    finally:
                        lock.release() 
                    
                    'trying a different library'
#                     response = requests.get(url)
#                     pageSource = response.text
#                     status_code = response.status_code
                    
                    urllib3.disable_warnings()
                    http = urllib3.PoolManager()
                    try:
                        response = http.request('GET', url)
                        pageSource = str(response.data)
                        status_code = response.status
                    except Exception:
                        pageSource = 'This page isn’t working'
                        status_code = int(200)
                    
                    print(' ^^^^^^^^^^^^^^^^^ status_code ====> ', status_code, '  url ===> '+url)
                                
                    if(str(status_code).startswith('4') | str(status_code).startswith('5')):
                        
                        print('Found a non responsive page  ==> '+url + " status code ==> ", status_code)
                        
                        lock = threading.RLock()
                        lock.acquire(blocking=True)
                        try:            
                            self.damnPagesMap.update({url : status_code})
                        finally:
                            lock.release()
                            
                    elif(pageSource.__contains__('DAMN!!')):
                        print('Found a DAMN Page  ==> '+url)
                            
                        lock = threading.RLock()
                        lock.acquire(blocking=True)
                        try:            
                            self.damnPagesMap.update({url : 'DAMN'})
                        finally:
                            lock.release()
                    
                    elif(pageSource.__contains__("This page isn’t working")):
                        print("This page isn't working ==> "+url)
                             
                        lock = threading.RLock()
                        lock.acquire(blocking=True)
                        try:            
                            self.damnPagesMap.update({url : 'Not_Working_Page'})
                        finally:
                            lock.release()
                                                    
                    else:
                        ''' apply regex to get urls from response - urls starting with http '''
                        urlList = re.findall('(?<=href=").*?(?=")', pageSource)
                        
                        ''' update the global url set and list '''
                        lock = threading.RLock()
                        lock.acquire(blocking=True)
                        try:
                            'convert received urls into set for uniqueness and map and remove non http urls + already browsed urls'
                            for x in urlList:
                                if ( (x.startswith('http')) & (self.ifLenskartDomain(x)) & ((self.globalUrlMap.get(x) == None) | (self.globalUrlMap.get(x) == False)) ):
                                    self.globalUrlMap.update({x:False})
                                else:
                                    urlList.remove(x)

                            print('After Updating traversed ==> ',len(self.globalTraversedSet), ' global map ==> ', len(self.globalUrlMap), ' global DAMN map ==> ' , len(self.damnPagesMap))
                                                    
                        except Exception:
                            traceback.print_exc(file=sys.stdout)
                            
                        finally:
                            lock.release()
                            
                except Exception:
                    print('exception occurred with url ==> ' +url)
                    traceback.print_exc(file=sys.stdout)
                    
#             print('final global traversed set ==> ',len(self.globalTraversedSet), ' global map ==> ', len(self.globalUrlMap), ' global DAMN map ==> ' , len(self.damnPagesMap))
            
        except Exception:
            traceback.print_exc(file=sys.stdout)


