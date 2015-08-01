import xml.etree.ElementTree as ET
import urllib.request as ur
import urllib.parse as up
import requests
import codecs
import sys

import comment_fetcher.CommentData as CD

class CommentFetcher:

    MAX_INT = sys.maxsize
    INVALID_ID = "NaN"
    
    def __init__(self):
        self.__yt_id = None
        self.__limit = CommentFetcher.MAX_INT
        self.__total_nof_comments = CommentFetcher.MAX_INT
        self.__curr_uri = None
        self.__next_uri = None
        self.__nof_comments = 0
        self.__comments = []
        self.__needs_update = True
    
    def __api_construct(self):
        uri =  "https://gdata.youtube.com/feeds/api/videos/"
        uri += self.__yt_id
        uri += "/comments?v=2" # API version 2
        uri += "&max-results=50" # default: 25, max: 50
        uri += "&orderby=published" # alternative: relevance
        uri += "&start-index=1"
        uri += "&prettyprint=true" # for debugging purposes
        #uri += "&alt=json"
        
        return uri
    
    @staticmethod
    def extract_youtube_id(url):
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        
        # give credit where credit is due: http://stackoverflow.com/a/7936523
        query = up.urlparse(url)
        if query.hostname == 'youtu.be':
            # http://youtu.be/YOUTUBE-ID&key_n=val_n
            return query.path[1:]
        if query.hostname == 'm.youtube.com':
            if not query.query:
                # http://m.youtube.com/#/watch?v=YOUTUBE-ID&key_n=val_n
                p = up.parse_qs(query.fragment)
                return p['/watch?v'][0]
            else:
                # http://m.youtube.com/watch?v=YOUTUBE-ID&key_n=val_n
                p = up.parse_qs(query.query)
                return p['v'][0]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                # http://www.youtube.com/watch?v=YOUTUBE-ID&key_n=val_n
                p = up.parse_qs(query.query)
                return p['v'][0]
            if query.path[:7] == '/embed/':
                # http://www.youtube.com/embed/YOUTUBE-ID&key_n=val_n
                return query.path.split('/')[2]
            if query.path[:3] == '/v/':
                # http://www.youtube.com/v/YOUTUBE-ID?key_n=val_n
                return query.path.split('/')[2]
        
        return CommentFetcher.INVALID_ID
    
    def __get_rid_of_utf8_bullshit(self, text):
        u_text = None
        if text is not None:
            u_text = text.encode('utf-8')
            if u_text.endswith(codecs.BOM_UTF8):
                u_text = u_text[:-len(codecs.BOM_UTF8)]
            u_text = u_text.decode('utf-8')
        return u_text
    
    def __get_request(self, url):
        root, next_url = None, None

        # assuming that we're dealing with a valid url
        r = requests.get(url)

        # tour-de-conditional
        if r.status_code == 200:
            # parse as xml
            root = ET.fromstring(r.text)
            for child in root:
                    if child.tag.endswith('link'):
                        items = child.items()
                        is_next = False
                        tmp = None

                        # can't trust them indexes
                        # loop over the attributes (rel = next) ...
                        for i in range(len(items)):
                            if items[i][1] == 'next':
                                is_next = True
                                break

                        # ... and retrieve assigned value (href = tmp)
                        if is_next:
                            for i in range(len(items)):
                                if items[i][0] == 'href':
                                    tmp = child.items()[i][1]
                                    break
                        
                        if tmp is not None and tmp.startswith("http") \
                           and CommentFetcher.is_valid_url(tmp):
                            next_url = tmp
                            break
                        
        return root, next_url
      
    def set_yt_id(self, yt_id):
        self.__yt_id = yt_id
    
    def set_yt_id_from_url(self, url):
        tmp_id = CommentFetcher.extract_youtube_id(url)
        
        if tmp_id == CommentFetcher.INVALID_ID:
            raise ValueError("Invalid YouTube URL.", url)
        else:
            self.__yt_id = tmp_id
    
    def set_limit(self, limit):
        self.__limit = limit
    
    def get_yt_id(self):
        return self.__yt_id
    
    def get_total_nof_comments(self):
        if self.__total_nof_comments == CommentFetcher.MAX_INT:
            if self.__root is not None:
                for child in self.__root:
                    if child.tag.endswith('totalResults'):
                        return int(child.text)
        
        return self.__total_nof_comments
    
    def get_comments(self):
        return self.__comments
    
    def initialize(self):
        uri = self.__api_construct()
        if not CommentFetcher.is_valid_url(uri):
            raise ValueError("Invalid YouTube URL or ID.")
        else:
            self.__curr_uri = uri
        self.update()
    
    def has_more(self):
        if self.__curr_uri is None or \
           self.__nof_comments >= min(self.__limit, self.get_total_nof_comments()):
            return False
        return True
       
    def process(self):
        if self.__needs_update:
            self.update()
        
        if self.__root is not None:
            for child in self.__root:
                if child.tag.endswith('entry'):
                    
                    author, content = None, None
                    publish_date, mod_date = None, None
                    gplus_id, channel_id = None, None
                    reply_count = None
                    
                    for entry in child:
                        if entry.tag.endswith('author'):
                            for name in entry:
                                if name.tag.endswith('name'):
                                    author = self.__get_rid_of_utf8_bullshit(name.text)
                        elif entry.tag.endswith('content'):
                            content = self.__get_rid_of_utf8_bullshit(entry.text)
                        elif entry.tag.endswith('published'):
                            publish_date = self.__get_rid_of_utf8_bullshit(entry.text)
                        elif entry.tag.endswith('updated'):
                            mod_date = self.__get_rid_of_utf8_bullshit(entry.text)
                        elif entry.tag.endswith('googlePlusUserId'):
                            gplus_id = self.__get_rid_of_utf8_bullshit(entry.text)
                        elif entry.tag.endswith('channelId'):
                            channel_id = self.__get_rid_of_utf8_bullshit(entry.text)
                    
                    comment = CD.CommentData(author, content, publish_date, mod_date, \
                                             gplus_id, channel_id)
                    self.__comments.append(comment)
                    
                    self.__nof_comments += 1
                    if self.__nof_comments >= self.__limit:
                        break
        
        self.__curr_uri = self.__next_uri
        self.__needs_update = True
    
    def update(self):
        if self.__curr_uri is not None:
            self.__root, self.__next_uri = self.__get_request(self.__curr_uri)
        
        self.__needs_update = False
    
    def clear(self):
        self.__comments = []
    
    @staticmethod
    def is_valid_url(url):
        try:
            ur.urlopen(url)
        except:
            # we end up here when url is either total gibberish
            # or we get status code from the server other than 200 OK
            return False
        return True
    