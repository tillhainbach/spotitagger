# spotitagger
Add metadata to your local audio files using Spotify's metadatabase

# installation and setup
This project supports only python3! 

open a terminal and run:
```
git clone https://github.com/tillhainbach/spotitagger

cd spotitagger

python -m venv .

pip install -r requirements.txt
```

# usage
```
python spotitagger.py -p "your spotify playlist id/uri/url" -f "path/to/your/musicfiles"
```

Only M4A/MP4 audiofiles are supported, at the moment.

# Contributions
The idea of this project arose from this repo: https://github.com/ritiek/spotify-downloader

I use an adaption of this pull request of spotipy: https://github.com/plamere/spotipy/pull/342

You can find the spotipy original repo here: https://github.com/plamere/spotipy





