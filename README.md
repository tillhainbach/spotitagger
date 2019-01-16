# spotitagger
Add metadata to your local audio files using Spotify's metadatabase

# installation and setup
This project is tested only for python >=3.6! 

In a terminal run:
```
git clone https://github.com/tillhainbach/spotitagger
```
to clone this repository.

Change into the repository directory:
```
cd spotitagger
```

Create a virtual environment for this repository. This is not necessary but it keeps your python clean and avoids conflicts between different versions of used modules.
```
python -m venv .
```

Activate the virtual environment.
```
source activate/bin
```

Install all required packages.
```
pip install -r requirements.txt
```


# usage
Activate the virtual environment.
```
source activate/bin
```
```
python spotitagger.py -p yourspotifyplaylistid/uri/url -f path/to/your/musicfiles
```

you can add a default folder and username (and other options) to config.yml

Only M4A/MP4 audiofiles are supported, at the moment.

# Contributions
The idea of this project arose from this repo: https://github.com/ritiek/spotify-downloader

I use an adaption of this pull request of spotipy: https://github.com/plamere/spotipy/pull/342

You can find the spotipy original repo here: https://github.com/plamere/spotipy





