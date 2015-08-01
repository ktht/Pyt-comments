import unittest
import comment_fetcher.CommentFetcher as CF

class TestYouTubeIDFromLink(unittest.TestCase):
    
    YT_ID = "YOUTUBE-ID"
    
    def create_uri_list(path, yt_id, kvs, include_www = True):
        uri_list = []
        schemas = ["http://", "https://", ""]
        wwws = [""]
        if include_www: wwws.append("www.")
        for schema in schemas:
            for www in wwws:
                for kv in kvs:
                    uri = schema + www + path + yt_id + kv
                    uri_list.append(uri)
        return uri_list
    
    def test_default_url(self):
        uri_list = TestYouTubeIDFromLink.create_uri_list("youtube.com/watch?v=", \
                                                         TestYouTubeIDFromLink.YT_ID, \
                                                         ["", "&k=v"])
        for uri in uri_list:
            yt_id = CF.CommentFetcher.extract_youtube_id(uri)
            self.assertEqual(yt_id, self.YT_ID)
    
    def test_embed_url(self):        
        uri_list = TestYouTubeIDFromLink.create_uri_list("youtube.com/embed/", \
                                                         TestYouTubeIDFromLink.YT_ID, \
                                                         ["", "?k=v", "?k=v&kn=vn"])
        for uri in uri_list:
            yt_id = CF.CommentFetcher.extract_youtube_id(uri)
            self.assertEqual(yt_id, self.YT_ID)
    
    def test_v_url(self):
        uri_list = TestYouTubeIDFromLink.create_uri_list("youtube.com/v/", \
                                                         TestYouTubeIDFromLink.YT_ID, \
                                                         ["", "?k=v", "?k=v&kn=vn"])
        for uri in uri_list:
            yt_id = CF.CommentFetcher.extract_youtube_id(uri)
            self.assertEqual(yt_id, self.YT_ID)
    
    def test_short_url(self):
        uri_list = TestYouTubeIDFromLink.create_uri_list("youtu.be/", \
                                                         TestYouTubeIDFromLink.YT_ID, \
                                                         ["", "?k=v", "?k=v&kn=vn"], \
                                                         False)
        for uri in uri_list:
            yt_id = CF.CommentFetcher.extract_youtube_id(uri)
            self.assertEqual(yt_id, self.YT_ID)
    
    def test_mobile_url(self):
        uri_list_1 = TestYouTubeIDFromLink.create_uri_list("m.youtube.com/#/watch?v=", \
                                                           TestYouTubeIDFromLink.YT_ID, \
                                                           ["", "&k=v"], \
                                                           False)
        uri_list_2 = TestYouTubeIDFromLink.create_uri_list("m.youtube.com/watch?v=", \
                                                           TestYouTubeIDFromLink.YT_ID, \
                                                           ["", "&k=v"], \
                                                           False)
        uri_list = uri_list_1 + uri_list_2
        
        for uri in uri_list:
            yt_id = CF.CommentFetcher.extract_youtube_id(uri)
            self.assertEqual(yt_id, self.YT_ID)
    

if __name__ == '__main__':
    unittest.main()