# Funny Joke Adventure (Desktop)

A tiny, kid-friendly, replayable joke game for ages ~4+ (with parent help). SPACE fetches a new clean joke (JokeAPI safe-mode). Offline fallback keeps the fun going without internet.

## Run

```bash
python -m venv .venv
# mac/linux:
source .venv/bin/activate
# windows:
# .venv\Scripts\activate

pip install -r requirements.txt
python game.py --tts --chaos 0.2

