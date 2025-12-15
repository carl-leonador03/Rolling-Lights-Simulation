# Streamlit for web app framework
import streamlit as st
# For visualizing the wheel
import matplotlib.pyplot as plt
# For math-related functions and utilities
import numpy as np
# For graph data generation
import pandas as pd
# For animation delay
import time
# For the game models
import simulation as sim

# Initialize important variables into session_state to persist on current session.
st.session_state.NUM_BULBS = st.session_state.get("NUM_BULBS", 12)
st.session_state.RADIUS = st.session_state.get("RADIUS", 1.0)
st.session_state.WEIGHTS = st.session_state.get("WEIGHTS", [])
st.session_state.SPIN_SPEED = st.session_state.get("SPIN_SPEED", 0.07)

st.session_state.PRIZE_POLL = st.session_state.get(
    "PRIZE_POLL",
    [np.random.choice(sim.Game.c) for _ in range(st.session_state.NUM_BULBS)]
)

st.session_state.is_tweaked_game = st.session_state.get("is_tweaked_game", False)
st.session_state.balance = st.session_state.get("balance", 2000)
st.session_state.bet = st.session_state.get("bet", 0)
st.session_state.bet_amount = st.session_state.get("bet_amount", 250)
st.session_state.house_bank = st.session_state.get("house_bank", 10000)

st.session_state.current = st.session_state.get("current", 0)
st.session_state.result_prize = st.session_state.get("result_prize", None)

# Helper function to redistribute probability weights on change
def on_weight_change(light):
    """Helper function to redistribute probability weights on change."""
    # Redistribute weights change across N bulbs
    changed_weight = st.session_state.WEIGHTS[light]
    other_weights = sum(
        [st.session_state.WEIGHTS[i] for i in range(len(st.session_state.WEIGHTS)) if i != light]
    ) * 100
    k = float((1 - changed_weight) / other_weights)

    # It follows the following function:
    # w_light = weight_changed
    # w_light + sum(P(l) for l in lights if l != light)k = 1
    # Solve for k.
    # for i in lights: if i != light: w[i] = w[i] * k

    for l in range(len(st.session_state.WEIGHTS)):
        if l != light:
            st.session_state.WEIGHTS[l] = (st.session_state.WEIGHTS[l] * 100) * k
    
    if sum(st.session_state.WEIGHTS) != 1.0:
        st.session_state.WEIGHTS[light] += (1 - sum(st.session_state.WEIGHTS))

def draw_wheel(active_index, highlight = False):
    """Helper function to draw the wheel."""
    fig, ax = plt.subplots(figsize = (5.5, 5.5))
    fig.patch.set_facecolor("#111111")
    ax.set_facecolor("#111111")

    # Draw outer and inner rings
    ax.add_artist(plt.Circle((0, 0), st.session_state.RADIUS, fill = False, # pyright: ignore[reportPrivateImportUsage]
                             linewidth = 4, color = "white"))

    ax.add_artist(plt.Circle((0, 0), st.session_state.RADIUS * 0.7, fill = False, # pyright: ignore[reportPrivateImportUsage]
                             linewidth = 2, color = "#777"))

    # Compute the angles for bulb placement
    angles = np.linspace(0, 2 * np.pi, st.session_state.NUM_BULBS, endpoint = False) + np.pi / 2

    for i, angle in enumerate(angles):
        # Bulb position
        bx, by = st.session_state.RADIUS * np.cos(angle), st.session_state.RADIUS * np.sin(angle)

        # Prize label position
        tx, ty = 0.55 * st.session_state.RADIUS * np.cos(angle), 0.55 * st.session_state.RADIUS * np.sin(angle)

        # Bulb label position
        btx, bty = 0.75 * st.session_state.RADIUS * np.cos(angle), 0.75 * st.session_state.RADIUS * np.sin(angle)

        # Draw bulb (highlight active bulb)
        if i == active_index:
            ax.scatter(bx, by, s = 1000, c = "yellow", alpha = 0.4)
            ax.scatter(bx, by, s = 550, c = "yellow",
                       edgecolors = "gold", linewidth = 2.5)
        
        else:
            ax.scatter(bx, by, s = 350, c = "#222",
                       edgecolors = "white", linewidth = 1.5)
        
        # Rotate prize text
        rotation = np.degrees(angle) - 90

        # Highlight winning prize if applicable
        color = "gold" if highlight and i == active_index else "white"
        weight = "bold" if highlight and i == active_index else "normal"

        # Draw prize text
        ax.text(
            tx, ty, f"${st.session_state.PRIZE_POLL[i]}",
            ha = "center", va = "center",
            rotation = rotation, rotation_mode = "anchor",
            color = color,
            fontweight = weight, fontsize = 11
        )

        # Draw bulb numbers
        ax.text(
            btx, bty, i, # type: ignore
            ha = "center", va = "center",
            rotation = rotation, rotation_mode = "anchor",
            color = color,
            fontweight = weight, fontsize = 11
        )

    # Final formatting
    ax.axis("off")
    ax.set_aspect("equal")
    return fig

# Toggle switch for tweaked game
st.toggle("Tweaked Game", key = "is_tweaked_game")

# Game settings collapsible
with st.expander(":material/edit: Game settings"):
    st.session_state.balance = st.number_input(
        "Player balance", 0, value = st.session_state.balance, icon = ":material/money_bag:"
    )
    st.session_state.house_bank = st.number_input(
        "House Bank balance", 1000, value = st.session_state.house_bank, icon = ":material/account_balance:"
    )

    st.html("<b>Wheel settings</b>")
    st.number_input("Number of bulbs", 12, 24, key = "NUM_BULBS", icon = ":material/lightbulb:")
    if len(st.session_state.WEIGHTS) != st.session_state.NUM_BULBS:
        st.session_state.WEIGHTS = [
            1 / st.session_state.NUM_BULBS for i in range(st.session_state.NUM_BULBS)
        ]
    st.number_input("Wheel radius", 1.0, key = "RADIUS", icon = ":material/circle:")
    st.number_input("Spin speed", 0.0, key = "SPIN_SPEED", icon = ":material/pace:")

    st.html("<b>Prize Poll settings</b>")
    with st.container(horizontal = True):
        for l in range(st.session_state.NUM_BULBS):
            st.session_state.PRIZE_POLL[l] = st.number_input(f"Bulb #{l}",
                                                             value = st.session_state.PRIZE_POLL[l],
                                                             min_value = 20,
                                                             max_value = 1000,
                                                             step = 10,
                                                             icon = ":material/attach_money:")
    
    st.html("<b>Tweaked Game settings</b>")

    st.info("Due to floating point precision, the total number of probability weights declared may not always equate to 1.0, as per required by `np.random.choice`'s `p` parameter. You can fine adjust the weights to fix this.", icon = ":material/info:")

    g = pd.DataFrame([st.session_state.WEIGHTS])
    st.bar_chart(g, horizontal = True, x_label = "", sort = True)

    st.write(f"Total: {sum(st.session_state.WEIGHTS)}")

    with st.container(horizontal = True):
        for l in range(st.session_state.NUM_BULBS):
            st.session_state.WEIGHTS[l] = st.number_input(f"Bulb #{l}",
                                                          value = st.session_state.WEIGHTS[l],
                                                          min_value = 0.0, max_value = 1.0,
                                                          disabled = not st.session_state.is_tweaked_game,
                                                          on_change = on_weight_change, args = [l],
                                                          format = "%.17f")

# Empty container for wheel rendering
wheel = st.empty()

with st.container(border = True, horizontal = True):
    # Current player balance
    balance = st.metric(":material/money_bag: Balance", f"${st.session_state.balance}")
    
    # House bank balance
    house_bank = st.metric(":material/account_balance: House Bank", f"${st.session_state.house_bank}")

    # Bet input
    with st.container(border = True):
        st.number_input("Bet amount", 10, key = "bet_amount", icon = ":material/attach_money:")
        st.number_input("Bet bulb", 0, st.session_state.NUM_BULBS - 1, key = "bet", icon = ":material/lightbulb:")
        
        if st.button("Spin", icon = ":material/casino:", type = "primary", use_container_width = True):
            if st.session_state.balance < st.session_state.bet_amount:
                st.error("Insufficient balance", icon = ":material/error:")

            else:
                # Initialize game object
                if not st.session_state.is_tweaked_game:
                    game = sim.FairGame(st.session_state.NUM_BULBS, st.session_state.house_bank,
                                        st.session_state.PRIZE_POLL)
                else:
                    game = sim.TweakedGame(st.session_state.NUM_BULBS, st.session_state.WEIGHTS,
                                           st.session_state.house_bank, st.session_state.PRIZE_POLL)
                
                # Define PRIZE_POLL
                # st.session_state.PRIZE_POLL = game.prize_poll
                
                # Perform bet
                game.bet(1, st.session_state.bet_amount, st.session_state.bet)

                # Deduct balance from bet amount:
                st.session_state.balance -= st.session_state.bet_amount

                # Number of animation steps
                # spins = np.random.randint(25, 45)

                reward = game.play()

                # Spin animation loop
                for i in range((st.session_state.NUM_BULBS * 3) + (game.selected + 1)):
                    st.session_state.current = i % st.session_state.NUM_BULBS
                    wheel.pyplot(draw_wheel(st.session_state.current))
                    time.sleep(st.session_state.SPIN_SPEED + 1 * 0.003)
                
                # Get outcome from game object.
                # Add to balance, if won.
                idx = game.selected
                
                if st.session_state.bet == idx:
                    prize = st.session_state.PRIZE_POLL[idx]
                    st.session_state.balance += prize
                    st.session_state.result_prize = prize

                st.session_state.house_bank = game.initial_bank

                # Display prize result, if won
                if st.session_state.bet == st.session_state.current:
                    if st.session_state.result_prize:
                        if st.session_state.result_prize == 1000:
                            st.balloons() # Jackpot effect
                        st.success(f"Prize won: ${st.session_state.result_prize}", icon = ":material/award_star:")
                else:
                    st.error(f"Sorry! You didn't won.", icon = ":material/sentiment_dissatisfied:")

# Render final wheel state
wheel.pyplot(
    draw_wheel(
        st.session_state.current,
        highlight = st.session_state.result_prize is not None
    )
)
