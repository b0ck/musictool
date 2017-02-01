"""Tool for calculating the average rating of albums in a folder and its sub-folders.
Takes root folder(s) as command line argument(s).
"""

import statistics
import taglib
import os
import sys

ratings_text = {1: 'Worst ever',
                2: 'Pure shit',
                3: 'Very bad',
                4: 'Bad',
                5: 'Not good',
                6: 'Average',
                7: 'Good',
                8: 'Very good',
                9: 'Excellent',
                10: 'Perfect'}


class Song:
    def __init__(self, track, title, album, rating):
        self.track = int(track)
        self.title = title
        self.album = album
        self.rating = int(rating)

    def trim(self, string):
        maxl = 20
        return (string[:maxl-3] + '...') if len(string) > maxl else string

    def __str__(self):
        return f"{self.track:0{2}d} | {self.trim(self.title):{20}} | " \
               f"{self.trim(self.album):{20}} | {'*' * self.rating}"


def get_tag(song, key, default):
    return song.tags.get(key, [default])[0]


def scan_file(path):
    song = taglib.File(path)

    return Song(track=get_tag(song, 'TRACKNUMBER', 0),
                title=get_tag(song, 'TITLE', '- No title -'),
                album=get_tag(song, 'ALBUM', '- No album -'),
                rating=get_tag(song, 'RATING', 0))


def scan_folder(root):
    songs = []

    print(f"{'#':{2}} | {'Title':{20}} | {'Album':{20}} | {'Rating'}")
    print('=' * 57)

    for path, subdirs, files in os.walk(root):
        for file in files:
            try:
                song = scan_file(os.path.join(path, file))
                print(song)
                songs.append(song)
            except:
                pass

    # create a dict that saves the song ratings for each album
    album_ratings = {}
    for song in songs:
        if song.album not in album_ratings:
            album_ratings[song.album] = []

        if song.rating > 0:
            album_ratings[song.album].append(song.rating)

    for album in album_ratings:
        if album_ratings[album]:
            rating = statistics.mean(album_ratings[album]) * 2
            print(f'{album}: {rating:{0}.{2}f} ({rating:{0}.{0}f}/10) '
                  f'-> {ratings_text[round(rating)]}')
        else:
            print(f'Album {album!r} has no ratings.')


def main():
    for arg in sys.argv[1:]:
        print(f'Scanning {arg!r}...')
        scan_folder(arg)


if __name__ == "__main__":
    main()
