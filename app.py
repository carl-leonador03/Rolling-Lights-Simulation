# ================== IMPORTS ==================
# Streamlit is used to build the interactive web app
import streamlit as st

# Matplotlib is used to draw the wheel visualization
import matplotlib.pyplot as plt

# NumPy handles probability modeling and random selection
import numpy as np

# Pandas is used for data aggregation and analysis in simulations
import pandas as pd

# Time is used to create animation delays
import time

# Random is used only for visual spin length (not probability logic)
import random

# Simulation contains the game models and the simulator for the web app
import simulation as sim

# ======== PAGES SETUP =============
# This section defines and includes the pages for the web apps.
pg = st.navigation(
    [
        st.Page("home.py", title = "Home", icon = ":material/house:"),
        st.Page("play.py", title = "Play Game", icon = ":material/sports_esports:"),
        st.Page("simulate.py", title = "Simulate", icon = ":material/play_circle:")
    ]
)


# ================== PAGE STYLE ==================
# Inject custom CSS to style the Streamlit app
# This controls background color, text alignment, and button size
st.markdown("""
<style>
body { background-color: #0e0e0e; }
h1, h2, h3 { text-align: center; }
button { height: 3em; width: 100%; font-size: 18px; }
</style>
""", unsafe_allow_html=True)

# Main application title
st.title(":material/attractions: Stochastic Bulb Wheel Game")

pg.run()