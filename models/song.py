class Song(object):

    def __init__(self, track, title, album, rating):
        """

        :param track:
        :param title:
        :param album:
        :param rating:
        """

        self.track = int(track)
        self.title = title
        self.album = album
        self.rating = int(rating)

    def trim(self, string):
        """

        :param string:
        :return:
        """

        maxl = 20
        return (string[:maxl-3] + '...') if len(string) > maxl else string

    def __str__(self):
        return f"{self.track:0{2}d} | {self.trim(self.title):{20}} | " \
               f"{self.trim(self.album):{20}} | {'*' * self.rating}"
