import feedparser
import requests
import json

PATH = "/movies"
PROFILE_ID = 4
APIKEY = " "


class Letterboxd:
    def __init__(self, url):
        self.feed = feedparser.parse(url)

    def list_titles(self):
        list = []
        for x in self.feed.entries:
            list.append(x.get('letterboxd_filmtitle'))
        return list


class Radarr:
    def __init__(self, url, port, apikey):
        self.server = f"{url}:{port}"
        self.apikey = apikey

    def list_titles(self):
        list = []
        movies = requests.get(
            f"http://{self.server}/api/movie?apikey={self.apikey}")
        for x in movies.json():
            list.append(x.get('title'))
        return list

    def search_movie(self, movie):
        url = f"http://{self.server}/api/movie/lookup?term={movie}&apikey={self.apikey}"
        response = requests.get(url)
        try:
            return response.json()[0]
        except BaseException:
            print(f"No movies found with name provided: '{movie}'")

    def add_movie(self, movie):
        user_pref = {
            'rootFolderPath': PATH,
            'profileID': PROFILE_ID,
            'monitored': True}
        body = movie
        body.update(user_pref)
        url = f"http://{self.server}/api/movie?apikey={self.apikey}"
        add = requests.post(url, data=json.dumps(body))
        return add


class Sync:
    def __init__(self, feed_url, radarr_url, radarr_port):
        self.feed = Letterboxd(feed_url)
        self.radarr = Radarr(radarr_url, radarr_port, APIKEY)

    def start(self):
        for x in self.feed.list_titles():
            if x not in self.radarr.list_titles():
                movie = self.radarr.search_movie(x)
                self.radarr.add_movie(movie)


sync = Sync('https://letterboxd.com/noquarteer/rss/', 'localhost', 7878)
Sync.start()
