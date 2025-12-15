import streamlit as st
import simulation as sim
import pandas as pd

# Initialize constants and variables in persistent session token.
st.session_state.NUM_BULBS = st.session_state.get('NUM_BULBS', 12)
st.session_state.SESSION_RUNS = st.session_state.get('SESSION_RUNS', 10000)
st.session_state.SEED = st.session_state.get('SEED', 42)
st.session_state.WEIGHTS = st.session_state.get('WEIGHTS', [])
st.session_state.BET = st.session_state.get('BET', 0)

def on_weight_change(light):
    # Redistribute weights change across N bulbs
    changed_weight = st.session_state.WEIGHTS[light]
    other_weights = sum([st.session_state.WEIGHTS[i] for i in range(len(st.session_state.WEIGHTS)) if i != light]) * 100
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

with st.expander(":material/edit: Modify simulation parameters"):
    st.markdown("<b>Global simulation settings</b>", unsafe_allow_html = True)

    with st.container():
        st.number_input("Number of Bulbs", 12, 24, key = "NUM_BULBS", icon = ":material/lightbulb:")
        if len(st.session_state.WEIGHTS) != st.session_state.NUM_BULBS:
            st.session_state.WEIGHTS = [1 / st.session_state.NUM_BULBS for i in range(st.session_state.NUM_BULBS)]
        st.number_input("Number of Simulations", 10000, step = 1000, key = "SESSION_RUNS", icon = ":material/timer_play:")
        st.number_input("Random Seed", value = 42, key = "SEED", icon = ":material/potted_plant:")
        st.number_input("Bet on:", key = st.session_state.BET, min_value = 0,
                        max_value = st.session_state.NUM_BULBS, icon = ":material/casino:")
    
    st.markdown("<b>Tweaked game settings</b>", unsafe_allow_html = True)
    st.info("Due to floating point precision, the total number of probability weights declared may not always equate to 1.0, as per required by `np.random.choice`'s `p` parameter. You can fine adjust the weights to fix this.", icon = ":material/info:")

    g = pd.DataFrame([st.session_state.WEIGHTS])
    st.bar_chart(g, horizontal = True, x_label = "", sort = True)

    st.write(f"Total: {sum(st.session_state.WEIGHTS)}")

    with st.container(horizontal = True):
        for l in range(st.session_state.NUM_BULBS):
            st.session_state.WEIGHTS[l] = st.number_input(f"Bulb #{l}", min_value = 0.0, max_value = 1.0,
                        value = st.session_state.WEIGHTS[l], on_change = on_weight_change,
                        args = [l], format = "%.17f")

if st.button("Simulate", icon = ":material/play_circle:", type = "primary"):
    with st.spinner("Running simulation...", show_time = True):
        FG = sim.FairGame(st.session_state.NUM_BULBS)
        TG = sim.TweakedGame(st.session_state.NUM_BULBS, st.session_state.WEIGHTS)

        # Bet
        FG.bet(1, 250, st.session_state.BET)
        TG.bet(1, 250, st.session_state.BET)

        fair_sim = sim.Simulator(FG, st.session_state.SESSION_RUNS, st.session_state.SEED)
        tweaked_sim = sim.Simulator(TG, st.session_state.SESSION_RUNS, st.session_state.SEED)

    a = [x for x in fair_sim.simulate()]
    b = [y for y in tweaked_sim.simulate()]

    with st.spinner("Fetching results..."):
        player_profit_fair = 0
        player_profit_tweaked = 0

        cumm_player_profit_fair = []
        cumm_player_profit_tweaked = []
        
        for z in a:
            if z != {}:
                player_profit_fair += z[1]
            else:
                player_profit_fair -= 250
            
            cumm_player_profit_fair.append(player_profit_fair)
        
        for z in b:
            if z != {}:
                player_profit_tweaked += z[1]
            else:
                player_profit_tweaked -= 250
            
            cumm_player_profit_tweaked.append(player_profit_tweaked)
        
        player_profits_fair = {'-250': 0, '250': 0}
        player_profits_tweaked = {'-250': 0, '250': 0}

        for z in a:
            if z == {}: player_profits_fair['-250'] += 1
            else: player_profits_fair['250'] += 1
        
        for z in b:
            if z == {}: player_profits_tweaked['-250'] += 1
            else: player_profits_tweaked['250'] += 1

        fair_win_rate = (len(a) - a.count({})) / len(a)
        tweaked_win_rate = (len(b) - b.count({})) / len(b)

        house_edge_fair = (fair_sim.game.initial_bank / st.session_state.SESSION_RUNS) / 250 * 100
        house_edge_tweaked = (tweaked_sim.game.initial_bank / st.session_state.SESSION_RUNS) / 250 * 100

        st.header(":material/analytics: Results")

        # =====> Game results <=======
        with st.container(horizontal = True):
            # Fair Game Results
            with st.container(border = True):
                st.markdown("<h2>Fair Game Results</h2>", unsafe_allow_html = True)
                st.table(
                    {
                        "Metrics": ["Win Rate:", "Total Profit:", "Avg. Profit per Round:", "House Edge:"],
                        "Results": [
                            f"{fair_win_rate * 100:.2f}%", f"${player_profit_fair:.2f}", f"${player_profit_fair / st.session_state.SESSION_RUNS:.2f}", f"{house_edge_fair:.2f}%"
                        ]
                    },
                    border = False
                )
            
            # Tweaked Game Results
            with st.container(border = True):
                st.html("<h2>Tweaked Game Results</h2>")
                st.table(
                    {
                        "Metrics": ["Win Rate:", "Total Profit:", "Avg. Profit per Round:", "House Edge:"],
                        "Results": [
                            f"{tweaked_win_rate * 100:.2f}%", f"${player_profit_tweaked:.2f}", f"${player_profit_tweaked / st.session_state.SESSION_RUNS:.2f}", f"{house_edge_tweaked:.2f}%"
                        ]
                    },
                    border = False
                )

        # ============ EDA ANALYSIS =============
        # Cummulative Player Profits
        with st.container(border = True):
            st.html("<b>Cummulative Player Profits Over Time</b>")
            
            cumm_player_profits = pd.DataFrame(
                [
                    { "Fair Game": fg, "Tweaked Game": tg } for fg, tg in zip(cumm_player_profit_fair, cumm_player_profit_tweaked)
                ]
            )

            # Delete these since it's no longer necessary to keep these in memory.
            del cumm_player_profit_fair
            del cumm_player_profit_tweaked

            st.line_chart(data = cumm_player_profits, x_label = "Rounds", y_label = "Profits ($)")

        # Profit Distribution Comparison
        with st.container(border = True):
            st.html("<b>Profit Distribution Comparison</b>")

            with st.container(horizontal = True):
                with st.container():
                    st.write("Fair Game Profit Distribution")
                    st.bar_chart(pd.DataFrame([player_profits_fair]), stack = False, y_label = "Frequency")
                
                with st.container():
                    st.write("Tweaked Game Profit Distribution")
                    st.bar_chart(pd.DataFrame([player_profits_tweaked]), stack = False, y_label = "Frequency")
        
        # House Edge & Win Rate
        with st.container(border = True):
            st.html("<b>House Edge and Win Rate</b>")
            with st.container(horizontal = True):
                with st.container():
                    st.write("House Edge")
                    st.bar_chart(
                        pd.DataFrame(
                            {
                                "Fair Game": [house_edge_fair,],
                                "Tweaked Game": [house_edge_tweaked,]
                            }
                        ),
                        stack = False, y_label = "Perrcent (%)"
                    )

                with st.container():
                    st.write("Win Rate")
                    st.bar_chart(
                        pd.DataFrame(
                            {
                                "Fair Game": [fair_win_rate * 100,],
                                "Tweaked Game": [tweaked_win_rate * 100,]
                            }
                        ),
                        stack = False, y_label = "Perrcent (%)"
                    )

