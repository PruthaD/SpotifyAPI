import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import csv
import pandas
import json
import re

client_id = '08948d34937146768e380e166f34ee5a'
secret = '0ed8b2790dc946d88d74eccbcb45e62b'

client_credential_manager = SpotifyClientCredentials(client_id=client_id, client_secret=secret)

sp = spotipy.Spotify(client_credentials_manager=client_credential_manager)

def getTrackResults(query):
    """
    :param query: year, for example 'year:2018'; or string such as 'Top 100' tracks
    :return: a Pandas Dataframe of top 100 tracks and their artists and popularity score
    """
    artists = []
    songs = []
    song_id = []
    popularity = []

    for i in range(0, 100, 50): #spotify only lets you query 50 records at a time, so setting range upto 100 with 50 as offset
        result = sp.search(query, limit=50, offset=i) #default type='track' per Spotify API docs
        for x, y in enumerate(result['tracks']['items']):
            songs.append(y['name'])
            artists.append(y['artists'][0]['name'])
            popularity.append(y['popularity'])
            song_id.append(y['id'])

    #writing output as csv for unit testing purpose
    # with open('./data/Top100TracksOutput.csv', 'w') as f:
    #     header = ['song_id','song','artist','popularity']
    #     writer = csv.writer(f)
    #     writer.writerow(header)
    #     writer.writerows(zip(song_id,songs,artists,popularity))
    # f.close()

    #Writing lists to Pandas dataframe as well for returning it as a result.
    df = pandas.DataFrame(
        {
            'song_id':song_id,
            'song':songs,
            'artist':artists,
            'popularity':popularity
        }
    )
    #print(df)

    return df


def getArtistAlbums(artist):
    """
    :param artist: artist name
    :return: top 1 album of a given artist
    """
    value = ''
    for i in range(0,1):
        result = sp.search('artist:'+artist,offset=i,type='album',limit=1)
        #print(result['albums']['items'])
        for x,y in enumerate(result['albums']['items']):
            value = y["name"]
    return value


def getPlaylists(query):
    """
    :param query: get user playlists with keyword as query
    :return: a Pandas dataframe with playlists, playlist_ids and total tracks per playlist
    """
    playlist_name = []
    total_tracks = []
    playlist_id = []

    for i in range(0, 100, 50):
        result = sp.search(query, limit=50, type='playlist',offset=i)
        #print(json.dumps(result, indent=4, sort_keys=True))
        for i, t in enumerate(result['playlists']['items']):
            total_tracks.append(t['tracks']['total'])
            playlist_name.append(t['name'])
            playlist_id.append(t['id'])

    #writing initial results to csv to show Special characters like Imojis in the data
    with open('./data/PlaylistsOutput_withSpecialChars.csv', 'w') as f:
        header = ['playlist_id','playlist_name','total_tracks']
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(zip(playlist_id,playlist_name,total_tracks))
    f.close()

    #Writing lists to Pandas dataframe as well for returning it as a result.
    df = pandas.DataFrame(
        {
            'playlist_id':playlist_id,
            'playlist_name':playlist_name,
            'total_tracks':total_tracks
        }
    )

    return df


#get result from tracks
tracks = getTrackResults("year:2018")

#Drop 'song_id' column from tracks dataframe and write to csv
tracks.drop(columns='song_id').to_csv('./data/Top100tracks2018.csv',sep=",",index=False)

#print(tracks['artist'].unique())

#get Unique values from artist column
unique_artists = tracks['artist'].unique()

#Get Top album per artist and write the records to csv
with open('./data/ArtistAlbumsOutput.csv', 'w') as f:
    header = ['artist','album']
    w = csv.writer(f)
    w.writerow(header)
    for i in range(len(unique_artists)):
        artist_album = getArtistAlbums(unique_artists[i]) #call getArtistAlbums() with query parameter
        l = []
        l.append(unique_artists[i])
        l.append(artist_album)
        w.writerow(l)
f.close()


#get results from playlists where playlist name contains 'Top 100' keywords
OutputPlaylists = getPlaylists("Top 100")


#remove special characters from 'playlist_name' column
OutputPlaylists['playlist_name'] = OutputPlaylists['playlist_name'].map(lambda x: re.sub('([^\s\w]|_)+', '', x))


#print(OutputPlaylists)

#Sort playlists dataframe by 'total_tracks' column decending and write to csv
OutputPlaylists.sort_values(by=['total_tracks'],ascending=False).to_csv('./data/PlaylistsOutput.csv',sep=',',index=False)



