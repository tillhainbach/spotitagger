# spotitagger
Add metadata to your local audio files using Spotify's metadatabase

# installation and setup

open a terminal and run:
git clone https://github.com/tillhainbach/spotitagger

cd spotitagger

python -m venv .

pip install -r requirements.txt

# usage
python spotitagger.py -p "your spotify playlist id/uri/url" -f "path/to/your/musicfiles"

at the moment only M4A/MP4 audiofiles are supported



