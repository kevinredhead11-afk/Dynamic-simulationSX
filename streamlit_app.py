"""
Iron Chouquette - Flash Game Emulator with Streamlit
Uses Ruffle to run Flash games in modern browsers
"""

import streamlit as st
import base64
import urllib.request

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
    """Download SWF file from GitHub"""
    # Try different SWF files
    urls = [
        "https://raw.githubusercontent.com/ToaJannox/mt_archives/main/KadoKado/Games/Iron%20Chouquette/swf/temple.swf",
        "https://raw.githubusercontent.com/ToaJannox/mt_archives/main/KadoKado/Games/Iron%20Chouquette/swf/root.swf",
        "https://raw.githubusercontent.com/ToaJannox/mt_archives/main/KadoKado/Games/Iron%20Chouquette/swf/code.swf",
    ]

    for url in urls:
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                swf_data = response.read()
                if len(swf_data) > 100:  # Valid SWF file
                    return base64.b64encode(swf_data).decode(), url.split('/')[-1]
        except Exception:
            continue

    return None, None

swf_b64, filename = get_swf_data()

if swf_b64:
    # Ruffle player with direct ArrayBuffer loading
    ruffle_html = f"""
    <script src="https://cdn.jsdelivr.net/npm/@ruffle-rs/ruffle@latest/dist/ruffle.js"></script>
    <div style="margin: 20px 0;">
        <canvas id="ruffle-canvas" style="width: 100%; max-width: 600px; height: 400px; background: #f0f0f0; display: block; margin: 0 auto;"></canvas>
    </div>
    <script>
    (async () => {{
        // Initialize Ruffle
        await window.RufflePlayer.isSupported();
        const ruffle = window.RufflePlayer.newest();
        const player = ruffle.createPlayer();
        const canvas = document.getElementById('ruffle-canvas');
        canvas.parentNode.replaceChild(player, canvas);

        // Load SWF from base64
        const binaryString = atob('{swf_b64}');
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {{
            bytes[i] = binaryString.charCodeAt(i);
        }}

        // Load from data
        await player.load({{
            data: bytes.buffer,
        }});
    }})().catch(err => {{
        console.error('Ruffle error:', err);
        document.getElementById('ruffle-canvas').style.display = 'none';
        const msg = document.createElement('div');
        msg.style.cssText = 'color: red; padding: 20px; text-align: center;';
        msg.textContent = 'Failed to load game: ' + err.message;
        document.body.appendChild(msg);
    }});
    </script>
    """

    st.components.v1.html(ruffle_html, height=500)
    st.caption(f"Loaded: `{filename}`")
else:
    st.error("""
    ❌ Could not download game file from GitHub.

    This might be due to:
    - Network issues
    - GitHub rate limiting
    - File access problems

    Try refreshing the page or try again in a moment.
    """)

st.markdown("---")
st.markdown("""
### About Iron Chouquette
A classic tower defense / strategy game with French pastry flair! 🥐

**Controls:** Check in-game instructions

**Note:** This is a Flash game emulated with Ruffle. Performance may vary.
Ruffle is still in active development, so some games may not work perfectly.
""")
