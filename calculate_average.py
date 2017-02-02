"""
Tool for calculating the average rating of albums in a folder and its sub-folders.
Takes root folder(s) as command line argument(s).
"""

import statistics
import taglib
import os
import sys
from models.song import Song
from logic.multiprocessing import MultiProcessing


class FileScanner(MultiProcessing):

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

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_tag(song, key, default):
        """

        :param song:
        :param key:
        :param default:
        :return:
        """

        return song.tags.get(key, [default])[0]

    def scan_file(self, file_path):
        """

        :param file_path:
        :return:
        """

        song = taglib.File(file_path)
        return Song(
                track=self.get_tag(song, 'TRACKNUMBER', 0), title=self.get_tag(song, 'TITLE', '- No title -'),
                album=self.get_tag(song, 'ALBUM', '- No album -'), rating=self.get_tag(song, 'RATING', 0)
            )

    def scan_folder(self, root_folder):
        """

        :param root_folder:
        :return:
        """

        print(f"{'#':{2}} | {'Title':{20}} | {'Album':{20}} | {'Rating'}")
        print('=' * 57)

        for path, subdirs, files in os.walk(root_folder):
            for file in files:
                try:
                    song = self.scan_file(os.path.join(path, file))
                    print(song)
                    self.song_list.append(song)
                except Exception as ex:
                    #print(ex)
                    pass

    def get_album_data(self, song):
        """

        :param song:
        :return:
        """

        if song.album not in self.album_ratings:
            self.album_ratings[song.album] = []

        if song.rating > 0:
            self.album_ratings[song.album].append(song.rating)

    def create_album_rating(self, album):
        """

        :param album:
        :return:
        """

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
            self.scan_folder(root_folder=root_folder)
            self.run_queued_method('get_album_data', self.song_list)
            self.run_queued_method('create_album_rating', self.album_ratings)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        print(f'Scanning {arg!r}...')
        scanner = FileScanner()
        scanner.scan_library(arg)
