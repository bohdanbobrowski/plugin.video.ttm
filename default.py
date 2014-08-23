# -*- coding: utf-8 -*-
import hashlib
import json
import os
import re
import time
import urllib
import urllib2
import xbmcaddon
import xbmcgui
import xbmcplugin

# TTM - plugin do XBMC
# by Bohdan Bobrowski 2014

addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')
addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
if not os.path.isdir(addonUserDataFolder):
    os.mkdir(addonUserDataFolder)
linki = {}  

def ListaKategorii():
        req = urllib2.Request('http://www.telewizjattm.pl/nasze-programy.html')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        html=response.read()
        response.close()
        match=re.compile('<a href="([^"]*)" class="program [a-z\s]*" title="([^"]*)" ><img src="([^"]*)" alt="[^"]*" /></a>').findall(html)
        categories = []
        for href,title,src in match:
            category = [title,href,src]
            categories.append(category)
            addDir(title,href,'http://www.telewizjattm.pl/' + src,1)
        categories_json = json.dumps(categories)
        categories_file = open(addonUserDataFolder + "/categories.json", "w")
        categories_file.write(categories_json)
        categories_file.close()

def ListaFilmow(url,name,page):
        url = url.replace('?play=on','')
        # url = url.replace('.html','/2-strona.html')        
        url_to_page = re.compile('(nasze-programy/[0-9]{1,3}-[a-z\-]*)').findall(url)[0]
    
        url = 'http://www.telewizjattm.pl/' + url
        print "Url: "+url

        m = hashlib.md5()
        m.update(url+time.strftime("%Y%m%d"))
        cache_hash = m.hexdigest()

        print "Url: "+str(url)
        print "Name: "+str(name)
        print "Strona: "+str(page)        
        if os.path.isfile(addonUserDataFolder + "/"+cache_hash+".json"):
            # Wczytaj cache, o ile istnieje:
            cache = {}
            with open(addonUserDataFolder + "/"+cache_hash+".json", "r") as f:
                for line in f:
                    line = str(line)
                    cache.update(json.loads(line))
            cache_l = cache['linki']
            cache_p = cache['podstrony']
            linki = []
            for l in cache_l:
                linki = linki + [str(l)]
            podstrony = []
            for p in cache_p:
                podstrony = podstrony + [str(p)]
        else:
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)
            html = response.read()
            response.close()
            linki = [] + re.findall('<li>[^>^<]*<a href="(nasze-programy[^"]*)" title="[^"]*"',html)
            podstrony = re.findall('<a href="('+url_to_page+'[^"]*)" class="page">[0-9]*</a>',html)
            # Zapisz cache:
            cache = {} 
            cache['linki'] = linki
            cache['podstrony'] = podstrony
            cache_json = json.dumps(cache)
            cache_file = open(addonUserDataFolder + "/"+cache_hash+".json", "w")
            cache_file.write(cache_json)
            cache_file.close()        
        # Sprawdzamy czy plik podręcznej pamięci już istnieje - jeżeli tak wczytujemy go, by przyspieszyć odczywalnie działanie wtyczki
        videos = {}
        if os.path.isfile(addonUserDataFolder + "/videos.json"):
            with open(addonUserDataFolder + "/videos.json", "r") as f:
                for line in f:
                    videos.update(json.loads(line))            
        for h in linki:
            video_url = 'http://www.telewizjattm.pl/' + h
            m = hashlib.md5()
            m.update(video_url)
            url_hash = m.hexdigest()
            if videos.get(url_hash) is not None:
                if videos[url_hash]:
                    addLink(videos[url_hash]['title'], videos[url_hash]['file'], 'http://www.telewizjattm.pl/' + videos[url_hash]['thumb']) 
            else:
                req_v = urllib2.Request(video_url)            
                req_v.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response_v = urllib2.urlopen(req_v)
                html_v = response_v.read()
                response_v.close()
                miniatura = re.compile('image: "([^"]*)",').findall(html_v)
                plikwideo = re.compile('file:"(http\:\/\/www\.telewizjattm\.pl\/ttm_filmy\/_new\/[^"]*[\.flv|.mp4])"').findall(html_v)
                tytul = re.compile('<span class="date"[\s]*>([^<^>]*)<\/span>[\s]*<h2 class="title">([^<^>]*)<\/h2>').findall(html_v)
                if miniatura and miniatura[0] and plikwideo and plikwideo[0] and tytul and tytul[0]:
                    videos[url_hash] = {}
                    videos[url_hash]['title'] = tytul[0][0] + " - " + tytul[0][1]
                    videos[url_hash]['file'] = plikwideo[0]
                    videos[url_hash]['thumb'] = miniatura[0]
                    addLink(tytul[0][0] + " - " + tytul[0][1], plikwideo[0], 'http://www.telewizjattm.pl/' + miniatura[0]) 
                else:
                    videos[url_hash] = False
        if len(podstrony) >= page:
            next_page_url = url_to_page+'/'+str(page+1)+'-strona.html'
            if name.find(' - Strona') > -1:
                name = name.split(' - Strona');
                name = name[0]
            addPageLink(name+" - Strona "+str(page+1), next_page_url, page+1)

        # Cache z informacjami o plikach wideo:
        videos_json = json.dumps(videos)
        videos_file = open(addonUserDataFolder + "/videos.json", "w")
        videos_file.write(videos_json)
        videos_file.close()        

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
        return param

def addLink(name,url,iconimage):
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addPageLink(name,url,page):
        u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+'&page='+str(page)
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png")
        liz.setInfo( type="Video", infoLabels={ "Title": name })
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addDir(name,url,iconimage,page):
        u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+'&page='+str(page)
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
              
params=get_params()
url=None
name=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
try:
        page=int(params["page"])
except:
        pass

if url==None or len(url)<1:
        ListaKategorii()
       
else:
        ListaFilmow(url,name,page)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
