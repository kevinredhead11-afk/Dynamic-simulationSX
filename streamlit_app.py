"""
Iron Chouquette - Flash Game Emulator with Streamlit
Uses Ruffle to run Flash games in modern browsers
"""

import streamlit as st
import base64

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

# Ruffle player HTML
ruffle_html = """
<script src="https://unpkg.com/@ruffle-rs/ruffle"></script>
<div style="display: flex; justify-content: center; margin: 20px 0;">
    <div id="ruffle-container" style="width: 300px; height: 320px; background: #fff; border: 2px solid #ccc; display: flex; align-items: center; justify-content: center;">
        <p>Loading game...</p>
    </div>
</div>
<script>
window.RufflePlayer = window.RufflePlayer || {};
window.addEventListener("load", () => {
    const ruffle = window.RufflePlayer.newest();
    const player = ruffle.createPlayer();
    const container = document.getElementById("ruffle-container");
    container.appendChild(player);
    player.load({
        url: "https://raw.githubusercontent.com/ToaJannox/mt_archives/main/KadoKado/Games/Iron%20Chouquette/swf/temple.swf"
    });
});
</script>
"""

st.components.v1.html(ruffle_html, height=380)

st.markdown("---")
st.markdown("""
### About Iron Chouquette
A classic tower defense / strategy game with French pastry flair! 🥐

**Controls:** Check in-game instructions

**Note:** This is a Flash game emulated with Ruffle. Performance may vary.
If the game doesn't load, try refreshing the page.
""")
