import streamlit as st
from mplsoccer import Sbopen, Pitch
import pandas as pd
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(page_title="Player Pass Analysis", layout="wide")
st.title("Football Player Pass Analysis System")

# Create parser object
parser = Sbopen()

# Load competitions data
@st.cache_data
def load_competitions():
    try:
        return parser.competition()
    except Exception as e:
        st.error(f"Error loading competitions: {str(e)}")
        return pd.DataFrame()

# Load matches data
@st.cache_data
def load_matches(comp_id, season_id):
    try:
        return parser.match(competition_id=comp_id, season_id=season_id)
    except Exception as e:
        st.error(f"Error loading matches: {str(e)}")
        return pd.DataFrame()

# Load match events
@st.cache_data
def load_events(match_id):
    try:
        df, _, _, _ = parser.event(match_id=match_id)
        return df
    except Exception as e:
        st.error(f"Error loading match events: {str(e)}")
        return pd.DataFrame()

# Create pass map visualization
def create_pass_map(df_pass, player_name):
    try:
        pitch = Pitch(line_color='black', pitch_type='statsbomb')
        fig, ax = pitch.draw(figsize=(12, 8))
        
        for _, row in df_pass.iterrows():
            color = 'green' if pd.isna(row['outcome_name']) else 'red'
            pitch.arrows(row['x'], row['y'], row['end_x'], row['end_y'],
                        color=color, ax=ax, width=2, headwidth=4, headlength=4)
            pitch.scatter(row['x'], row['y'], alpha=0.5, s=200, color=color, ax=ax)
        
        successful = df_pass['outcome_name'].isna().sum()
        failed = len(df_pass) - successful
        accuracy = successful / len(df_pass) * 100 if len(df_pass) > 0 else 0
        
        stats_text = f"Successful: {successful}\nFailed: {failed}\nAccuracy: {accuracy:.1f}%"
        ax.text(110, 80, stats_text, fontsize=12, color='black',
               ha='right', bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))
        
        plt.title(f"Pass Analysis for {player_name}\nGreen = Accurate   |   Red = Inaccurate", fontsize=14)
        return fig
    
    except Exception as e:
        st.error(f"Error creating pass map: {str(e)}")
        return None

def main():
    with st.sidebar:
        st.header("Match Selection")
        
        competitions = load_competitions()
        if not competitions.empty:
            selected_comp = st.selectbox(
                "Select Competition",
                competitions['competition_name'].unique(),
                key='comp_select'
            )
            
            comp_filter = competitions['competition_name'] == selected_comp
            filtered_seasons = competitions[comp_filter]
            
            selected_season = st.selectbox(
                "Select Season",
                filtered_seasons['season_name'].unique(),
                key='season_select'
            )
            
            season_filter = filtered_seasons['season_name'] == selected_season
            comp_id = filtered_seasons.loc[season_filter, 'competition_id'].iloc[0]
            season_id = filtered_seasons.loc[season_filter, 'season_id'].iloc[0]
            
            matches = load_matches(comp_id, season_id)
            
            if not matches.empty:
                selected_match = st.selectbox(
                    "Select Match",
                    matches.apply(lambda x: f"{x['home_team_name']} vs {x['away_team_name']} - {x['match_date']}", axis=1),
                    key='match_select'
                )
                
                match_idx = matches.apply(lambda x: f"{x['home_team_name']} vs {x['away_team_name']} - {x['match_date']}", axis=1) == selected_match
                match_id = matches.loc[match_idx, 'match_id'].iloc[0]
                
                events = load_events(match_id)
                
                if not events.empty:
                    players = events['player_name'].dropna().unique()
                    
                    # Searchable dropdown for players
                    selected_player = st.selectbox(
                        "Search and Select Player",
                        players,
                        index=None,
                        placeholder="Start typing to search...",
                        key='player_select'
                    )
                    
                    if selected_player and st.button("Show Pass Analysis"):
                        st.session_state.selected_player = selected_player
                else:
                    st.warning("No event data available for this match")
            else:
                st.warning("No matches available for this season")
        else:
            st.warning("No competitions available")
    
    if hasattr(st.session_state, 'selected_player'):
        st.header(f"Pass Analysis for: {st.session_state.selected_player}")
        
        mask_player = (events['type_name'] == 'Pass') & (events['player_name'] == st.session_state.selected_player)
        df_pass = events.loc[mask_player, ['x', 'y', 'end_x', 'end_y', 'outcome_name']]
        
        if not df_pass.empty:
            pass_map = create_pass_map(df_pass, st.session_state.selected_player)
            if pass_map:
                st.pyplot(pass_map)
                
                col1, col2, col3 = st.columns(3)
                successful_passes = df_pass['outcome_name'].isna().sum()
                total_passes = len(df_pass)
                
                with col1:
                    st.metric("Total Passes", total_passes)
                with col2:
                    st.metric("Successful Passes", successful_passes)
                with col3:
                    st.metric("Pass Accuracy", f"{(successful_passes/total_passes*100):.1f}%")
        else:
            st.warning("No pass data available for this player in the selected match")

if __name__ == "__main__":
    main()