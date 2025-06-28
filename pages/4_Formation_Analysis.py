import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

st.set_page_config(page_title="Counter Formation Predictor", layout="wide")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('merged2_output.csv')

        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def preprocess_data(df):
    try:
        df = df.drop(columns=['Opponent', 'Result', 'Winning Team'])
        df.fillna(0, inplace=True)

        for col in ['Winning Team Formation', 'Losing Team Formation']:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].str.encode('ascii', 'ignore').str.decode('ascii')

        winning_encoder = LabelEncoder()
        losing_encoder = LabelEncoder()
        df['Winning Team Formation'] = winning_encoder.fit_transform(df['Winning Team Formation'])
        df['Losing Team Formation'] = losing_encoder.fit_transform(df['Losing Team Formation'])

        df['Winning Team Goals'] = df['Winning Team Goals'].astype(str).str.extract(r'^(\d+)').astype(int)
        df['Losing Team Goals'] = df['Losing Team Goals'].astype(str).str.extract(r'^(\d+)').astype(int)

        df['Goal Diff'] = df['Winning Team Goals'] - df['Losing Team Goals']
        df['xG Diff'] = df['Winning Team xG'] - df['Losing Team xG']
        df['Close Game'] = (abs(df['Goal Diff']) <= 1).astype(int)
        df['Total Goals'] = df['Winning Team Goals'] + df['Losing Team Goals']

        return df, winning_encoder, losing_encoder
    except Exception as e:
        st.error(f"Error preprocessing data: {str(e)}")
        return df, None, None

def prepare_model_input(df):
    X = df[['Losing Team Formation', 'Winning Team Goals', 'Losing Team Goals',
            'Winning Team xG', 'Losing Team xG', 'Goal Diff', 'xG Diff', 'Close Game', 'Total Goals']]
    y = df['Winning Team Formation']

    counts = y.value_counts()
    valid_classes = counts[counts >= 2].index
    X = X[y.isin(valid_classes)]
    y = y[y.isin(valid_classes)]

    smote = SMOTE(random_state=42, k_neighbors=1)
    X_resampled, y_resampled = smote.fit_resample(X, y)

    return X_resampled, y_resampled

@st.cache_data
def train_model(X_train, y_train):
    try:
        rf_model = RandomForestClassifier(criterion='gini', n_estimators=100, max_depth=10, random_state=33)
        rf_model.fit(X_train, y_train)
        return rf_model
    except Exception as e:
        st.error(f"Error training model: {str(e)}")
        return None

def predict_counter_formation(user_formation, winning_encoder, losing_encoder, rf_model, median_values):
    encoded_input = losing_encoder.transform([user_formation])[0]
    input_data = [[
        encoded_input,
        median_values['winning_goals'],
        median_values['losing_goals'],
        median_values['winning_xg'],
        median_values['losing_xg'],
        median_values['goal_diff'],
        median_values['xg_diff'],
        median_values['close_game'],
        median_values['total_goals']
    ]]
    predicted_encoded = rf_model.predict(input_data)[0]
    predicted_formation = winning_encoder.inverse_transform([predicted_encoded])[0]
    return predicted_formation

#  MAIN 
def main():
    st.title("⚽ Counter Formation Predictor")

    page = st.sidebar.selectbox("📂 Select Page", ["🎯 Predict the Lineup", "📊 Model Evaluation"])

    df = load_data()
    if df.empty:
        st.warning("No data available.")
        return

    df, winning_encoder, losing_encoder = preprocess_data(df)
    X_resampled, y_resampled = prepare_model_input(df)
    X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=44)
    rf_model = train_model(X_train, y_train)

    median_values = {
        'winning_goals': df['Winning Team Goals'].median(),
        'losing_goals': df['Losing Team Goals'].median(),
        'winning_xg': df['Winning Team xG'].median(),
        'losing_xg': df['Losing Team xG'].median(),
        'goal_diff': df['Goal Diff'].median(),
        'xg_diff': df['xG Diff'].median(),
        'close_game': df['Close Game'].median(),
        'total_goals': df['Total Goals'].median()
    }

    if page == "🎯 Predict the Lineup":
        trained_formations = winning_encoder.inverse_transform(np.unique(y_resampled))
        user_formation = st.selectbox("Select your formation:", trained_formations)

        if st.button("🎯 Get Counter Formation"):
            predicted_formation = predict_counter_formation(
                user_formation, winning_encoder, losing_encoder, rf_model, median_values
            )
            st.session_state['user_formation'] = user_formation
            st.session_state['predicted_formation'] = predicted_formation

        if 'predicted_formation' in st.session_state:
            st.success(f"Suggested counter formation against **{st.session_state['user_formation']}** is: **{st.session_state['predicted_formation']}**")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Your Formation:** {st.session_state['user_formation']}")
            with col2:
                st.markdown(f"**Counter Formation:** {st.session_state['predicted_formation']}")

    elif page == "📊 Model Evaluation":
        st.header("📊 Model Evaluation Report")

        y_pred = rf_model.predict(X_test)
        y_test_names = winning_encoder.inverse_transform(y_test)
        y_pred_names = winning_encoder.inverse_transform(y_pred)

        report_dict = classification_report(y_test_names, y_pred_names, output_dict=True)
        report_df = pd.DataFrame(report_dict).transpose()

        st.dataframe(report_df.style.format("{:.2f}"))

if __name__ == "__main__":
    main()
