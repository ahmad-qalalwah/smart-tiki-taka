import streamlit as st
from statsbombpy import sb
import pandas as pd
from mplsoccer import Pitch
import matplotlib.pyplot as plt
import ast

# Page configuration
st.set_page_config(page_title="Football Shot Analysis", layout="wide")
st.title("Football Match Shot Analysis")

# Load competitions data
@st.cache_data
def load_competitions():
    try:
        return sb.competitions()
    except Exception:
        return pd.DataFrame()

# Load matches data
def load_matches(comp_id, season_id):
    try:
        cache_key = f"matches_{comp_id}_{season_id}"
        if cache_key not in st.session_state:
            st.session_state[cache_key] = sb.matches(competition_id=comp_id, season_id=season_id)
        return st.session_state[cache_key]
    except Exception:
        return pd.DataFrame()

# Load events data
def load_events(match_id):
    try:
        cache_key = f"events_{match_id}"
        if cache_key not in st.session_state:
            st.session_state[cache_key] = sb.events(match_id=match_id)
        return st.session_state[cache_key]
    except Exception:
        return pd.DataFrame()

# Create shot map
def create_shot_map(events_df, team1, team2):
    try:
        # Identify required columns dynamically
        required_cols = {
            'team': 'team' if 'team' in events_df.columns else 'team_name',
            'type': 'type' if 'type' in events_df.columns else 'type_name',
            'outcome': 'shot_outcome' if 'shot_outcome' in events_df.columns else 'outcome_name',
            'player': 'player' if 'player' in events_df.columns else 'player_name',
            'location': 'location' if 'location' in events_df.columns else None,
            'x': 'x' if 'x' in events_df.columns else None,
            'y': 'y' if 'y' in events_df.columns else None
        }

        shots = events_df[events_df[required_cols['type']] == 'Shot'].copy()
        if shots.empty:
            st.warning("No shot data available for this match")
            return None

        pitch = Pitch(line_color='black', pitch_type='statsbomb')
        fig, ax = pitch.draw(figsize=(12, 8))

        team1_shots = shots[shots[required_cols['team']] == team1]
        for _, shot in team1_shots.iterrows():
            try:
                if required_cols['x'] and required_cols['y'] and pd.notna(shot[required_cols['x']]) and pd.notna(shot[required_cols['y']]):
                    x, y = shot[required_cols['x']], shot[required_cols['y']]
                else:
                    loc = shot[required_cols['location']]
                    x, y = ast.literal_eval(loc) if isinstance(loc, str) else loc
                if shot[required_cols['outcome']] == 'Goal':
                    pitch.scatter(x, y, ax=ax, s=500, color='red', alpha=1)
                    pitch.annotate(str(shot[required_cols['player']]), (x+1, y-2), ax=ax, fontsize=12)
                else:
                    pitch.scatter(x, y, ax=ax, s=300, color='red', alpha=0.3)
            except Exception:
                continue

        team2_shots = shots[shots[required_cols['team']] == team2]
        for _, shot in team2_shots.iterrows():
            try:
                if required_cols['x'] and required_cols['y'] and pd.notna(shot[required_cols['x']]) and pd.notna(shot[required_cols['y']]):
                    x, y = shot[required_cols['x']], shot[required_cols['y']]
                else:
                    loc = shot[required_cols['location']]
                    x, y = ast.literal_eval(loc) if isinstance(loc, str) else loc
                if shot[required_cols['outcome']] == 'Goal':
                    pitch.scatter(120-x, 80-y, ax=ax, s=500, color='blue', alpha=1)
                    pitch.annotate(str(shot[required_cols['player']]), (120-x+1, 80-y-2), ax=ax, fontsize=12)
                else:
                    pitch.scatter(120-x, 80-y, ax=ax, s=300, color='blue', alpha=0.3)
            except Exception:
                continue

        plt.title(f"{team1} (Red) vs {team2} (Blue) - Shot Map", fontsize=16)
        return fig

    except Exception as e:
        return None

# Main app
def main():
    if 'analyze' not in st.session_state:
        st.session_state.analyze = False

    with st.sidebar:
        st.header("Match Selection")
        competitions = load_competitions()
        if not competitions.empty:
            selected_comp = st.selectbox("Select Competition", competitions['competition_name'].unique(), key='comp_select')
            filtered_seasons = competitions[competitions['competition_name'] == selected_comp]
            selected_season = st.selectbox("Select Season", filtered_seasons['season_name'].unique(), key='season_select')
            comp_id = filtered_seasons[filtered_seasons['season_name'] == selected_season]['competition_id'].iloc[0]
            season_id = filtered_seasons[filtered_seasons['season_name'] == selected_season]['season_id'].iloc[0]
            matches = load_matches(comp_id, season_id)

            if not matches.empty:
                st.markdown("### 🏟️ Available Matches")
                for idx, match in matches.iterrows():
                    match_label = f"{match['home_team']} vs {match['away_team']} - {match['match_date']}"
                    with st.expander(match_label):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**Venue:** {match.get('stadium', 'Unknown')}  \n"
                                        f"**Competition:** {selected_comp}  \n"
                                        f"**Season:** {selected_season}")
                        with col2:
                            if st.button("Analyze", key=f"analyze_{match['match_id']}"):
                                st.session_state.match_id = match['match_id']
                                st.session_state.home_team = match['home_team']
                                st.session_state.away_team = match['away_team']
                                st.session_state.analyze = True
                                st.rerun()
            else:
                st.warning("No matches available for this season")
                st.session_state.analyze = False
        else:
            st.warning("No competitions available")
            st.session_state.analyze = False

    if st.session_state.get('analyze', False):
        st.header(f"Shot Analysis: {st.session_state.home_team} vs {st.session_state.away_team}")
        with st.spinner("Loading match data..."):
            events = load_events(st.session_state.match_id)
            if not events.empty:
                shot_map = create_shot_map(events, st.session_state.home_team, st.session_state.away_team)
                if shot_map:
                    st.pyplot(shot_map)

                    # Identify actual column names dynamically
                    type_col = 'type_name' if 'type_name' in events.columns else 'type'
                    team_col = 'team_name' if 'team_name' in events.columns else 'team'
                    outcome_col = 'outcome_name' if 'outcome_name' in events.columns else 'shot_outcome'

                    home_shots = events[(events[type_col] == 'Shot') & (events[team_col] == st.session_state.home_team)]
                    away_shots = events[(events[type_col] == 'Shot') & (events[team_col] == st.session_state.away_team)]

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(f"{st.session_state.home_team} Shots", len(home_shots))
                        st.metric("Goals", len(home_shots[home_shots[outcome_col] == 'Goal']))
                    with col2:
                        st.metric(f"{st.session_state.away_team} Shots", len(away_shots))
                        st.metric("Goals", len(away_shots[away_shots[outcome_col] == 'Goal']))
                else:
                    st.warning("Could not generate shot map")
            else:
                st.warning("No event data available for this match")

if __name__ == "__main__":
    main()
