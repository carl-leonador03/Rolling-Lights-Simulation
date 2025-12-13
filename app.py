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
st.title("🎡 Stochastic Bulb Wheel Game")


# ================== CONSTANTS ==================
# Number of bulbs (possible outcomes)
NUM_BULBS = 12

# Radius of the wheel (used for plotting)
RADIUS = 1.0

# Base delay used for the spin animation
SPIN_SPEED = 0.07

# Cost of one spin in pesos
SPIN_COST = 250

# Number of simulations for Monte Carlo analysis
SIM_RUNS = 10000


# Prize values assigned to each bulb
# Bulb #1 starts at the top (12 o’clock position)
prizes = [
    1000, 100, 50, 100, 20, 500,
    50, 200, 750, 200, 20, 500
]


# ================== PROBABILITIES ==================
# FAIR GAME:
# Each bulb has equal probability (1/12)
fair_probs = np.ones(NUM_BULBS) / NUM_BULBS


# TWEAKED GAME (HOUSE EDGE):
# Weights are assigned based on prize value
# Smaller prizes appear more often, especially ₱20
weights = []
for p in prizes:
    if p == 20:
        weights.append(0.25)      # Highest probability
    elif p < 200:
        weights.append(0.15)
    elif p < 500:
        weights.append(0.08)
    else:
        weights.append(0.04)

# Normalize weights so total probability = 1
tweaked_probs = np.array(weights)
tweaked_probs = tweaked_probs / tweaked_probs.sum()


# ================== SESSION STATE ==================
# Streamlit reruns the script on every interaction.
# session_state is used to persist values across reruns.

# Current bulb index (used for animation and final result)
if "current" not in st.session_state:
    st.session_state.current = 0

# Player balance
if "balance" not in st.session_state:
    st.session_state.balance = 2000

# Last prize won (used for highlighting and result display)
if "result_prize" not in st.session_state:
    st.session_state.result_prize = None


# ================== DRAW WHEEL ==================
# This function draws the bulb wheel using Matplotlib.
# It does NOT determine outcomes — it is purely visual.
def draw_wheel(active_index, highlight=False):

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    fig.patch.set_facecolor("#111111")
    ax.set_facecolor("#111111")

    # Draw outer and inner rings of the wheel
    ax.add_artist(plt.Circle((0, 0), RADIUS, fill=False,
                             linewidth=4, color="white"))
    ax.add_artist(plt.Circle((0, 0), RADIUS * 0.7, fill=False,
                             linewidth=2, color="#666"))

    # Generate angles for bulb placement
    # + pi/2 ensures bulb #1 starts at the top (12 o’clock)
    angles = np.linspace(0, 2*np.pi, NUM_BULBS, endpoint=False) + np.pi / 2

    for i, angle in enumerate(angles):
        # Bulb position
        bx, by = RADIUS * np.cos(angle), RADIUS * np.sin(angle)

        # Prize label position (inside the wheel)
        tx, ty = 0.55 * RADIUS * np.cos(angle), 0.55 * RADIUS * np.sin(angle)

        # Draw bulb (highlight active bulb)
        if i == active_index:
            ax.scatter(bx, by, s=1000, c="yellow", alpha=0.4)
            ax.scatter(bx, by, s=550, c="yellow",
                       edgecolors="gold", linewidth=2.5)
        else:
            ax.scatter(bx, by, s=350, c="#222",
                       edgecolors="white", linewidth=1.5)

        # Rotate prize text to align radially
        rotation = np.degrees(angle) - 90

        # Highlight winning prize if applicable
        color = "gold" if highlight and i == active_index else "white"
        weight = "bold" if highlight and i == active_index else "normal"

        # Draw prize label
        ax.text(
            tx, ty, f"₱{prizes[i]}",
            ha="center", va="center",
            rotation=rotation,
            rotation_mode="anchor",
            color=color,
            fontweight=weight,
            fontsize=11
        )

    # Final formatting
    ax.axis("off")
    ax.set_aspect("equal")
    return fig


# ================== GAME UI ==================
# Select game mode (Fair or Tweaked)
mode = st.radio(
    "Game Mode",
    ["Fair Game", "Tweaked Game (House Edge)"],
    horizontal=True
)

# Placeholder for wheel rendering
placeholder = st.empty()

# Display current player balance
st.metric("💰 Balance", f"₱{st.session_state.balance}")

# Spin button
if st.button("🎲 Spin (-₱250)"):

    # Prevent spinning if balance is insufficient
    if st.session_state.balance < SPIN_COST:
        st.error("Insufficient balance")

    else:
        # Deduct spin cost
        st.session_state.balance -= SPIN_COST

        # Number of animation steps (purely visual)
        spins = random.randint(25, 45)

        # Spin animation loop
        for i in range(spins):
            st.session_state.current = (st.session_state.current + 1) % NUM_BULBS
            placeholder.pyplot(draw_wheel(st.session_state.current))
            time.sleep(SPIN_SPEED + i * 0.003)

        # Actual outcome selection using probabilities
        if mode == "Fair Game":
            idx = np.random.choice(range(NUM_BULBS), p=fair_probs)
        else:
            idx = np.random.choice(range(NUM_BULBS), p=tweaked_probs)

        # Update state with final result
        st.session_state.current = idx
        prize = prizes[idx]
        st.session_state.balance += prize
        st.session_state.result_prize = prize


# Render final wheel state
placeholder.pyplot(
    draw_wheel(
        st.session_state.current,
        highlight=st.session_state.result_prize is not None
    )
)

# Display prize result
if st.session_state.result_prize:
    if st.session_state.result_prize == 1000:
        st.balloons()  # Jackpot effect
    st.success(f"🎯 Prize Won: ₱{st.session_state.result_prize}")


# ================== MONTE CARLO SIMULATION ==================
st.divider()
st.header("📊 Monte Carlo Simulation (10,000 Plays)")

# Simulation function for repeated spins
def simulate(probs):
    balance = 0
    outcomes = []

    for _ in range(SIM_RUNS):
        balance -= SPIN_COST
        idx = np.random.choice(range(NUM_BULBS), p=probs)
        balance += prizes[idx]
        outcomes.append(prizes[idx])

    return balance, outcomes


# Run simulations for both game modes
if st.button("▶ Run Simulation"):

    fair_balance, fair_outcomes = simulate(fair_probs)
    tweaked_balance, tweaked_outcomes = simulate(tweaked_probs)

    # Count outcome frequencies (safe for Streamlit charts)
    counts_fair = pd.Series(fair_outcomes).value_counts().sort_index()
    counts_tweaked = pd.Series(tweaked_outcomes).value_counts().sort_index()

    chart_df = pd.DataFrame({
        "Fair Game": counts_fair,
        "Tweaked Game": counts_tweaked
    }).fillna(0)

    st.subheader("Outcome Distribution")
    st.bar_chart(chart_df)

    # House edge calculation
    fair_edge = (-fair_balance / SIM_RUNS) / SPIN_COST * 100
    tweaked_edge = (-tweaked_balance / SIM_RUNS) / SPIN_COST * 100

    st.subheader("House Edge")
    st.write(f"Fair Game House Edge: **{fair_edge:.2f}%**")
    st.write(f"Tweaked Game House Edge: **{tweaked_edge:.2f}%**")
