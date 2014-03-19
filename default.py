# -*- coding: utf-8 -*-
import urllib,urllib2,re,xbmcplugin,xbmcgui,json
# TTM - plugin do XBMC
# by Bohdan Bobrowski 2014

def ListaKategorii():
        req = urllib2.Request('http://www.telewizjattm.pl/nasze-programy.html')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        match=re.compile('<a href="([^"]*)" class="program [a-z\s]*" title="([^"]*)" ><img src="([^"]*)" alt="[^"]*" /></a>').findall(link)
        categories = []
        for href,title,src in match:
            addDir(title,href,'http://www.telewizjattm.pl/' + src,1)

def ListaFilmow(url,name):
        url = 'http://www.telewizjattm.pl/' + url
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        miniatura = re.compile('image: "([^"]*)",').findall(link)
        plikwideo = re.compile('file:"(http\:\/\/www\.telewizjattm\.pl\/ttm_filmy\/_new\/[^"]*[\.flv|.mp4])"').findall(link)
        tytul = re.compile('<span class="date"[\s]*>([^<^>]*)<\/span>[\s]*<h2 class="title">([^<^>]*)<\/h2>').findall(link)
        if miniatura and miniatura[0] and plikwideo and plikwideo[0] and tytul and tytul[0]:
            addLink(tytul[0][0] + " - " + tytul[0][1], plikwideo[0], 'http://www.telewizjattm.pl/' + miniatura[0])            
        linki = re.compile('</li>[\s]*<li><a href="([^"]*)" title').findall(link)
        for h in linki:
            url = 'http://www.telewizjattm.pl/' + h
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)
            link = response.read()
            response.close()
            miniatura = re.compile('image: "([^"]*)",').findall(link)
            plikwideo = re.compile('file:"(http\:\/\/www\.telewizjattm\.pl\/ttm_filmy\/_new\/[^"]*[\.flv|.mp4])"').findall(link)
            tytul = re.compile('<span class="date"[\s]*>([^<^>]*)<\/span>[\s]*<h2 class="title">([^<^>]*)<\/h2>').findall(link)
            if miniatura and miniatura[0] and plikwideo and plikwideo[0] and tytul and tytul[0]:
                addLink(tytul[0][0] + " - " + tytul[0][1], plikwideo[0], 'http://www.telewizjattm.pl/' + miniatura[0])            
                
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
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok


def addDir(name,url,iconimage,page):
        u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
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

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if url==None or len(url)<1:
        print ""
        ListaKategorii()
       
else:
        print ""+url
        ListaFilmow(url,name)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
