# Streamlit is used to build the interactive web app
import streamlit as st

# ======== PAGES SETUP =============
# This section defines and includes the pages for the web app.
pg = st.navigation(
    [
        st.Page("home.py", title = "Home", icon = ":material/house:"),
        st.Page("play.py", title = "Play Game", icon = ":material/sports_esports:"),
        st.Page("simulate.py", title = "Simulate", icon = ":material/play_circle:")
    ]
)

st.session_state.pages = pg

# ================== PAGE STYLE ==================
# Inject custom CSS to style the Streamlit app
# This controls background color, text alignment, and button size
st.markdown("""
<style>
body { background-color: #0e0e0e; }
button { height: 3em; width: 100%; font-size: 18px; }
</style>
""", unsafe_allow_html=True)

# Main application title
st.title(":material/attractions: Stochastic Bulb Wheel Game", text_alignment = "center")

pg.run()