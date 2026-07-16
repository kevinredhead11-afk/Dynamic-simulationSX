# Iron Chouquette 🍪

Play the classic Flash game **Iron Chouquette** in your browser using **Ruffle** (Flash emulator).

## What is this?

Iron Chouquette is a classic Flash game from the KadoKado series. This Streamlit app wraps it with Ruffle, an open-source Flash player that works in modern browsers.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open http://localhost:8501

## Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Connect your GitHub account
3. Deploy from:
   - **Repository:** `kevinredhead11-afk/Dynamic-simulationSX`
   - **Branch:** `claude/paper-learning-1568bn`
   - **Main file path:** `streamlit_app.py`

## About Ruffle

Ruffle is an open-source Flash emulator written in Rust and WebAssembly.
- **GitHub:** https://github.com/ruffle-rs/ruffle
- **Docs:** https://ruffle.rs/

## Limitations

- Games may run slower than original Flash Player
- Some advanced Flash features may not work
- Network/external API calls may not work
- Performance depends on browser and machine

## Original Game

Original source: https://github.com/ToaJannox/mt_archives/tree/main/KadoKado/Games/Iron%20Chouquette
