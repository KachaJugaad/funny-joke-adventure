# web/streamlit_app.py
import os
import io
import time
import base64
import random
import requests
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

# (Optional) pandas for local stats; skip if not available
try:
    import pandas as pd
except Exception:
    pd = None

# Optional TTS via gTTS (online). Falls back silently if unavailable.
try:
    from gtts import gTTS
except Exception:
    gTTS = None

SAFE_API_URL = "https://v2.jokeapi.dev/joke/Any?safe-mode&type=single"
OFFLINE_JOKES = [
    "Why did the teddy bear say no to dessert? Because it was stuffed!",
    "What do you call a sleeping bull? A bulldozer!",
    "Why did the banana go to the doctor? It wasn't peeling well.",
    "What do you call a boomerang that doesn't come back? A stick!",
    "Why did the cookie go to the nurse? It felt crummy.",
    "Why don't eggs tell jokes? They'd crack each other up!",
    "What do you call cheese that isn't yours? Nacho cheese!",
    "How do you make a lemon drop? Just let it fall.",
    "Why did the bicycle fall over? It was two-tired!",
    "Why did the student eat his homework? Because the teacher said it was a piece of cake!",
]

DENYLIST = set()  # e.g., {"die", "kill"}

def clean_joke(text: str) -> str:
    for w in DENYLIST:
        text = text.replace(w, "★" * len(w))
    return text

def fetch_joke(timeout=5.0):
    """Fetch a safe single-line joke; fallback to offline on error."""
    try:
        r = requests.get(SAFE_API_URL, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        joke = data.get("joke")
        if not isinstance(joke, str) or not joke.strip():
            raise ValueError("Malformed API response")
        return clean_joke(joke), "api"
    except Exception:
        return random.choice(OFFLINE_JOKES), "offline"

def tts_bytes(joke_text, lang="en"):
    """Return MP3 bytes for joke_text using gTTS (if available)."""
    if gTTS is None:
        return None
    try:
        tts = gTTS(text=joke_text, lang=lang)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception:
        return None

def write_log(row, path="logs/session_log.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    header_needed = not os.path.exists(path)
    with open(path, "a", encoding="utf-8") as f:
        if header_needed:
            f.write("timestamp,source,success,joke_len,session_id\n")
        f.write(",".join(map(str, [
            datetime.utcnow().isoformat()+"Z",
            row.get("source",""),
            row.get("success",""),
            row.get("joke_len",""),
            row.get("session_id",""),
        ])) + "\n")

# ----------------- THEME & STATE -----------------
st.set_page_config(page_title="Funny Joke Adventure", page_icon="🎈", layout="wide")

BALLOON_PALETTES = {
    "red":    ("#FF3B30", "#FF6B6B", "#FF8C00"),
    "blue":   ("#4D9EFF", "#2D6BFF", "#0047FF"),
    "green":  ("#21C55D", "#16A34A", "#0E7A36"),
    "purple": ("#A78BFA", "#7C3AED", "#5B21B6"),
    "pink":   ("#FF7EB3", "#FF4D6D", "#E6398A"),
    "teal":   ("#2DD4BF", "#14B8A6", "#0D9488"),
    "gold":   ("#FFD54F", "#FFB300", "#FF8F00"),
}
def random_palette():
    name = random.choice(list(BALLOON_PALETTES.keys()))
    return name, BALLOON_PALETTES[name]

# Session state
if "plays" not in st.session_state: st.session_state.plays = 0
if "session_id" not in st.session_state: st.session_state.session_id = f"web-{int(time.time())}"
if "last_joke" not in st.session_state: st.session_state.last_joke = ""
if "tts_on" not in st.session_state: st.session_state.tts_on = True
if "balloon_color" not in st.session_state:
    name, _ = random_palette()
    st.session_state.balloon_color = name
if "audio_seq" not in st.session_state: st.session_state.audio_seq = 0
if "audio_b64" not in st.session_state: st.session_state.audio_b64 = None
if "autoplay" not in st.session_state: st.session_state.autoplay = False

# Build CSS using the current balloon color
c1, c2, c3 = BALLOON_PALETTES[st.session_state.balloon_color]
SUPERMAN_BLUE = "#0F52BA"

st.markdown(f"""
<style>
/* Superman-blue background */
main, .stApp {{
  background: {SUPERMAN_BLUE} !important;
}}
.block-container {{
  padding-top: 1.0rem;
  max-width: 980px;
}}
.title {{
  text-align: center;
  font-size: 3rem;
  font-weight: 900;
  letter-spacing: 1px;
  color: #ffffff;
  text-shadow: 2px 2px 6px rgba(0,0,0,0.5);
}}
.joke-card {{
  background: #ffffffee;
  border: 4px solid #ffffff;
  border-radius: 24px;
  padding: 1.4rem;
  margin: 1rem auto;
  text-align: center;
  box-shadow: 0 8px 24px rgba(0,0,0,0.25);
  font-size: 2rem;
  color: #111;
}}
/* top-centered balloon */
.balloon-hold {{
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: .5rem;
  margin-bottom: .5rem;
}}
.balloon-btn button {{
  background: radial-gradient(circle at 30% 30%, {c1} 0%, {c2} 60%, {c3} 100%) !important;
  color: #fff !important;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.7) !important;
  border: none !important;
  border-radius: 999px !important;
  box-shadow: 0 10px 20px rgba(0,0,0,0.35) !important;
  padding: 1.2rem 2rem !important;
  font-size: 1.6rem !important;
  font-weight: 900 !important;
  letter-spacing: 0.5px;
  transition: transform 100ms ease-in-out;
}}
.balloon-btn button:hover {{ transform: scale(1.08) translateY(-3px); }}
.balloon-btn button:active {{ transform: scale(0.9); }}
.balloon-caption {{
  text-align: center;
  font-size: 1rem;
  font-weight: 800;
  color: #E5E7EB;
  margin-top: 0.3rem;
}}
</style>
""", unsafe_allow_html=True)

# ----------------- HEADER -----------------
st.markdown('<div class="title">Funny Joke Adventure 🎉</div>', unsafe_allow_html=True)
st.caption("Pop the balloon to hear and read a silly, kid-safe joke!")

# ----------------- BALLOON (fixed at top center) -----------------
st.markdown('<div class="balloon-hold">', unsafe_allow_html=True)
st.markdown('<div class="balloon-btn">', unsafe_allow_html=True)
popped = st.button("🎈 POP ME! 🎈", key="pop_button", use_container_width=False)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="balloon-caption">Tap to pop the balloon and get a new joke!</div>', unsafe_allow_html=True)

# ----------------- POP HANDLER -----------------
if popped:
    t0 = time.time()
    joke, src = fetch_joke(timeout=5.0)
    st.session_state.last_joke = joke
    st.session_state.plays += 1
    write_log({
        "source": src,
        "success": (src == "api"),
        "joke_len": len(joke),
        "session_id": st.session_state.session_id
    })
    # choose a new balloon color each pop (visual fun only)
    st.session_state.balloon_color, _ = random_palette()
    t1 = time.time()
    st.toast("POP! 🎈", icon="🎉")
    st.caption(f"Loaded in {t1 - t0:.2f}s • Source: {src.upper()}")

    # Prepare TTS for THIS joke and mark to autoplay on this render
    st.session_state.autoplay = False
    if st.session_state.tts_on:
        mp3 = tts_bytes(st.session_state.last_joke)
        if mp3:
            st.session_state.audio_b64 = base64.b64encode(mp3).decode()
            st.session_state.audio_seq += 1  # unique token to bust caching
            st.session_state.autoplay = True

# ----------------- JOKE DISPLAY -----------------
if st.session_state.last_joke:
    st.markdown(f"<div class='joke-card'>{st.session_state.last_joke}</div>", unsafe_allow_html=True)
else:
    st.markdown(
        "<div class='joke-card' style='font-size:1.6rem;'>Press <b>POP ME!</b> to start your adventure 🎈</div>",
        unsafe_allow_html=True
    )

# ----------------- FORCE PLAY AUDIO EVERY CLICK -----------------
# Use JS to reliably play the generated MP3 immediately after a user click.
if st.session_state.autoplay and st.session_state.audio_b64:
    # Unique token ensures the browser treats each play as fresh
    token = st.session_state.audio_seq
    components.html(f"""
        <script>
          (function() {{
            try {{
              const src = "data:audio/mp3;base64,{st.session_state.audio_b64}#seq={token}";
              const a = new Audio(src);
              a.play().catch(() => {{ /* ignore (browser policy), text still shows */ }});
            }} catch (e) {{}}
          }})();
        </script>
    """, height=0)
    # Reset the flag so we only autoplay once per pop
    st.session_state.autoplay = False

# ----------------- PARENT SETTINGS & STATS -----------------
with st.expander("Parent settings & session stats", expanded=False):
    st.session_state.tts_on = st.checkbox("Speak the joke aloud (web TTS)", value=st.session_state.tts_on)
    if pd is not None:
        col1, col2, col3 = st.columns(3)
        col1.metric("Plays this session", st.session_state.plays)
        csv_path = "logs/session_log.csv"
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                api_rate = (df["success"].mean()*100) if not df.empty else 0.0
                col2.metric("API success rate", f"{api_rate:.0f}%")
                col3.metric("Avg joke length", f"{df['joke_len'].mean():.0f} chars")
                with st.expander("Local log (anonymous, on this server only)"):
                    st.dataframe(df.tail(50), use_container_width=True, height=240)
            except Exception:
                pass
    else:
        st.write("Plays this session:", st.session_state.plays)

st.caption("Made with ❤️ for tiny humans. No ads. Safe jokes only (API safe-mode + offline list).")

