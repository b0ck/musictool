"""
Tool for calculating the average rating of albums in a folder and its sub-folders.
Takes root folder(s) as command line argument(s).
"""

import statistics
import taglib
import os
import sys
from models.song import Song


class FileScanner(object):

    ratings_text = {
        1: 'Worst ever',
        2: 'Pure shit',
        3: 'Very bad',
        4: 'Bad',
        5: 'Not good',
        6: 'Average',
        7: 'Good',
        8: 'Very good',
        9: 'Excellent',
        10: 'Perfect'
    }

    song_list = []
    album_ratings = {}

    @staticmethod
    def get_tag(song, key, default):
        """

        :param song:
        :param key:
        :param default:
        :return:
        """

        return song.tags.get(key, [default])[0]

    def scan_file(self, path):
        """

        :param path:
        :return:
        """

        song = taglib.File(path)
        self.song_list.append(
            Song(
                track=self.get_tag(song, 'TRACKNUMBER', 0), title=self.get_tag(song, 'TITLE', '- No title -'),
                album=self.get_tag(song, 'ALBUM', '- No album -'), ating=self.get_tag(song, 'RATING', 0)
            )
        )

    def scan_folder(self, root):
        """

        :param root:
        :return:
        """

        print(f"{'#':{2}} | {'Title':{20}} | {'Album':{20}} | {'Rating'}")
        print('=' * 57)

        for path, subdirs, files in os.walk(root):
            for file in files:
                try:
                    self.scan_file(os.path.join(path, file))
                except:
                    pass

    def get_albums(self):
        """

        :return:
        """

        for song in self.song_list:
            if song.album not in self.album_ratings:
                self.album_ratings[song.album] = []

            if song.rating > 0:
                self.album_ratings[song.album].append(song.rating)

    def create_album_ratings(self):
        """

        :return:
        """

        for album in self.album_ratings:
            if self.album_ratings[album]:
                rating = statistics.mean(self.album_ratings[album]) * 2
                print(f'{album}: {rating:{0}.{2}f} ({rating:{0}.{0}f}/10) '
                      f'-> {ratings_text[round(rating)]}')
            else:
                print(f'Album {album!r} has no ratings.')

    def scan_library(self, root_folder=None):
        """

        :param root_folder:
        :return:
        """

        if root_folder:
            self.scan_folder(root=root_folder)
            self.get_albums()
            self.create_album_ratings()


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        print(f'Scanning {arg!r}...')
        scanner = FileScanner()
        scanner.scan_library(arg)
