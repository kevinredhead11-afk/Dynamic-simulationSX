"""
Iron Chouquette - Flash Game Emulator with Streamlit
Uses Ruffle to run Flash games in modern browsers
"""

import streamlit as st
import base64
import urllib.request
import os

st.set_page_config(
    page_title="Iron Chouquette",
    page_icon="🍪",
    layout="centered"
)

st.title("🍪 Iron Chouquette")
st.markdown("*A classic Flash game, now playable in your browser*")

st.info("""
This game is powered by **Ruffle** — a Flash emulator in WebAssembly.
Games may run slower than the original Flash Player, but they should work!
""")

# Download and cache the SWF file
@st.cache_data
def get_swf_data():
    """Download SWF file from GitHub and return as base64"""
    url = "https://raw.githubusercontent.com/ToaJannox/mt_archives/main/KadoKado/Games/Iron%20Chouquette/swf/root.swf"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            swf_data = response.read()
        return base64.b64encode(swf_data).decode()
    except Exception as e:
        st.error(f"Failed to download game: {e}")
        return None

swf_b64 = get_swf_data()

if swf_b64:
    # Ruffle player HTML with embedded SWF as data URI
    ruffle_html = f"""
    <script src="https://cdn.jsdelivr.net/npm/@ruffle-rs/ruffle@latest/dist/ruffle.js"></script>
    <div style="display: flex; justify-content: center; margin: 20px 0;">
        <div id="ruffle-container" style="width: 600px; height: 400px; background: #fff; border: 2px solid #ccc;">
            <object
                data="data:application/x-shockwave-flash;base64,{swf_b64}"
                type="application/x-shockwave-flash"
                width="600"
                height="400"
                style="width: 100%; height: 100%;">
                <param name="allowScriptAccess" value="sameDomain" />
                <param name="quality" value="high" />
                <param name="wmode" value="direct" />
                <p>Flash game could not be loaded. Try a different browser or enable Flash support.</p>
            </object>
        </div>
    </div>
    <script>
    // Initialize Ruffle player
    window.RufflePlayer = window.RufflePlayer || {{}};
    window.RufflePlayer.config = {{
        autoplay: "on",
        unmuteOverlay: "hidden",
    }};
    </script>
    """

    st.components.v1.html(ruffle_html, height=450)
else:
    st.error("Could not load the game. Please refresh the page.")

st.markdown("---")
st.markdown("""
### About Iron Chouquette
A classic tower defense / strategy game with French pastry flair! 🥐

**Controls:** Check in-game instructions

**Note:** This is a Flash game emulated with Ruffle. Performance may vary.
If the game doesn't load, try:
- Refreshing the page
- Using Chrome/Firefox
- Allowing popups/scripts
""")
