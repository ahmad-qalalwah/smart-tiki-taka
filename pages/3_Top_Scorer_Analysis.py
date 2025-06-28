import streamlit as st
from mplsoccer import VerticalPitch
import pandas as pd
import matplotlib.pyplot as plt
from statsbombpy import sb

# Page configuration
st.set_page_config(page_title="Shot Analysis System", layout="wide", page_icon="⚽")
st.title("Football Shot Analysis - StatsBomb Data")

@st.cache_data
def get_available_competitions():
    """Get all available competitions from StatsBomb"""
    try:
        comps = sb.competitions()
        return comps[['country_name', 'competition_name', 'season_name', 'competition_gender', 'competition_id', 'season_id']]
    except Exception as e:
        st.error(f"Error loading competitions: {str(e)}")
        return pd.DataFrame()

def safe_extract_coordinates(df, col_name):
    """Safely extract coordinates from a column"""
    if col_name in df.columns:
        return df[col_name].apply(
            lambda loc: pd.Series({'x': loc[0], 'y': loc[1]}) if isinstance(loc, list) and len(loc) >= 2 
            else pd.Series({'x': None, 'y': None})
        )
    return pd.DataFrame({'x': [None]*len(df), 'y': [None]*len(df)})

# Sidebar UI
with st.sidebar:
    st.header("Data Selection")
    
    competitions_df = get_available_competitions()
    
    if not competitions_df.empty:
        countries = sorted(competitions_df['country_name'].unique())
        selected_country = st.selectbox("Select Country", countries, index=0)
        
        country_comps = competitions_df[competitions_df['country_name'] == selected_country]
        competitions = sorted(country_comps['competition_name'].unique())
        selected_comp = st.selectbox("Select Competition", competitions, index=0)
        
        comp_seasons = country_comps[country_comps['competition_name'] == selected_comp]
        seasons = sorted(comp_seasons['season_name'].unique(), reverse=True)
        selected_season = st.selectbox("Select Season", seasons, index=0)
        
        selected_data = comp_seasons[comp_seasons['season_name'] == selected_season].iloc[0]
        comp_id = selected_data['competition_id']
        season_id = selected_data['season_id']
        selected_gender = selected_data['competition_gender']

        # Get matches to retrieve teams
        try:
            matches_preview = sb.matches(competition_id=comp_id, season_id=season_id)
            if not matches_preview.empty:
                teams = sorted(set(matches_preview['home_team']).union(set(matches_preview['away_team'])))
                selected_team = st.selectbox("Select Team", teams)

                if st.button("Analyze Data"):
                    st.session_state.comp_id = comp_id
                    st.session_state.season_id = season_id
                    st.session_state.comp_name = selected_comp
                    st.session_state.season_name = selected_season
                    st.session_state.team = selected_team
        except Exception as e:
            st.error(f"Failed to load teams: {str(e)}")

# Data Processing
if hasattr(st.session_state, 'comp_id'):
    with st.spinner("Loading match data..."):
        try:
            matches = sb.matches(
                competition_id=st.session_state.comp_id,
                season_id=st.session_state.season_id
            )
            
            selected_team = st.session_state.team

            if not matches.empty:
                all_shots = []
                all_goals = []

                for i, match_id in enumerate(matches['match_id']):
                    try:
                        match = matches[matches['match_id'] == match_id].iloc[0]
                        if selected_team not in [match['home_team'], match['away_team']]:
                            continue

                        match_events = sb.events(match_id=match_id)

                        if not match_events.empty:
                            loc_data = safe_extract_coordinates(match_events, 'location')
                            match_events['x'] = loc_data['x']
                            match_events['y'] = loc_data['y']

                            shots = match_events[
                                (match_events['type'] == "Shot") & 
                                (match_events['shot_type'] != "Penalty") &
                                (match_events['x'].notna()) &
                                (match_events['team'] == selected_team)
                            ]
                            goals = shots[shots['shot_outcome'] == "Goal"]

                            all_shots.append(shots)
                            all_goals.append(goals)
                    except Exception as e:
                        st.warning(f"Couldn't process match {match_id}: {str(e)}")
                        continue

                if all_shots:
                    shots_df = pd.concat(all_shots)
                    goals_df = pd.concat(all_goals)

                    stats = []
                    for (player, team), group in shots_df.groupby(['player', 'team']):
                        stats.append({
                            'Player': player,
                            'Team': team,
                            'Shots': len(group),
                            'Goals': len(goals_df[goals_df['player'] == player]),
                            'xG': round(group['shot_statsbomb_xg'].sum(), 2)
                        })

                    stats_df = pd.DataFrame(stats).sort_values('xG', ascending=False)

                    st.header(f"Top Scorers - {selected_team} - {st.session_state.comp_name} {st.session_state.season_name}")
                    st.dataframe(stats_df.head(10))

                    selected_player = st.selectbox("Select player", stats_df['Player'])
                    if selected_player:
                        player_shots = shots_df[shots_df['player'] == selected_player]
                        player_goals = goals_df[goals_df['player'] == selected_player]

                        pitch = VerticalPitch(pitch_type='statsbomb', half=True)
                        fig, ax = pitch.draw(figsize=(12, 8))

                        if not player_shots.empty:
                            pitch.scatter(
                                player_shots['x'], player_shots['y'],
                                s=player_shots['shot_statsbomb_xg'] * 500 + 100,
                                c='red', alpha=0.6, label='Shots', ax=ax
                            )

                        if not player_goals.empty:
                            pitch.scatter(
                                player_goals['x'], player_goals['y'],
                                s=player_goals['shot_statsbomb_xg'] * 500 + 100,
                                c='white', edgecolors='blue',
                                marker='football', label='Goals', ax=ax
                            )

                        ax.legend(loc='center')
                        plt.title(f"{selected_player} Shot Map")
                        st.pyplot(fig)
                else:
                    st.warning("No shot data available for this team")
            else:
                st.warning("No matches found")
        except Exception as e:
            st.error(f"Error: {str(e)}")
