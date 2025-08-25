# Funny Joke Adventure — Streamlit MVP

A web-friendly MVP of the kid-safe, one-button joke game. Press the big button to fetch a clean joke (safe-mode) from JokeAPI. If the API is unavailable, the app falls back to an offline list. Optional voice is provided via gTTS.

## Run locally

```bash
python -m venv .venv
# mac/linux:
source .venv/bin/activate
# windows:
# .venv\Scripts\activate

pip install -r requirements.txt
streamlit run streamlit_app.py

