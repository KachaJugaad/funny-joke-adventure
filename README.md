# 🎈 Funny Joke Adventure

**Funny Joke Adventure** is a light-hearted, kids-friendly interactive web game built on [Streamlit](https://streamlit.io).  
Each play delivers a **fresh joke** from a real-time API, paired with colorful visuals and automatic narration — creating a simple, joyful adventure that never repeats the same way twice.

---

## 🌟 Product Summary

- **Problem**  
  Most kids’ digital activities are either repetitive or overly complex. Parents and caregivers want short, safe, and engaging digital experiences that spark laughter and curiosity without ads or distractions.

- **Solution**  
  Funny Joke Adventure creates a **safe, dynamic play loop**:
  - Fetches clean jokes from an open API (or offline fallback).  
  - Shows them with bright, balloon-themed UI.  
  - Narrates each joke aloud using text-to-speech (auto-plays after a balloon pop).  
  - Encourages replayability — every click brings a surprise.

- **Value Proposition**  
  - **For kids** → laughter, vocabulary exposure, sense of surprise.  
  - **For parents** → a safe, ad-free, hands-free game.  
  - **For portfolio/research** → demonstrates API integration, UI/UX tailoring, chaos testing, and deployment on Streamlit Cloud.

---

## 🛠️ Architecture & Tech Stack

- **Frontend**: Streamlit (custom CSS for balloon styling, animations).  
- **Backend**: Python 3.10, using `requests` for JokeAPI calls and `gTTS` for speech synthesis.  
- **Data Source**: [JokeAPI](https://jokeapi.dev) (safe-mode enabled).  
- **Deployment**: Streamlit Community Cloud.  
- **Resilience**: Offline fallback jokes + graceful error handling.  
- **Logging/Analytics**: Local session CSV logs (for demoing metrics such as API success rate).  

**Flow**:
1. User taps the balloon.  
2. App fetches a new joke (API → JSON).  
3. Joke displays in a speech bubble card.  
4. Audio plays immediately (TTS).  
5. Session logs capture play count and success rates.

---

## 📊 Metrics for Success

- **Engagement** → multiple replays per session.  
- **Content freshness** → high API success rate (>95%).  
- **Delight** → positive kid/parent feedback (laughter, retention).  
- **Reliability** → UI never freezes even if API fails (chaos-tested).

---

## 🚀 Running Locally

```bash
git clone https://github.com/KachaJugaad/funny-joke-adventure.git
cd funny-joke-adventure
pip install -r requirements.txt
streamlit run web/streamlit_app.py
