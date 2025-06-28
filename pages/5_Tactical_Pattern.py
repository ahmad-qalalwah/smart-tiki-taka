import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import make_pipeline

# Page configuration
st.set_page_config(page_title="Football Tactics Classifier", layout="wide")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('match_anlayze.csv')
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def preprocess_data(df):
    try:
        df = df.drop(columns=['match_id', 'competition', 'season', 'team', 'counter_attacks', 'successful_passes'])
        return df
    except Exception as e:
        st.error(f"Error preprocessing data: {str(e)}")
        return df

@st.cache_data
def perform_clustering(df):
    try:
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df)
        kmeans_model = KMeans(n_clusters=5, init='k-means++', random_state=33, algorithm='lloyd')
        kmeans_model.fit(scaled_data)
        df['Cluster'] = kmeans_model.labels_
        cluster_names = {
            0: 'Balanced High Press',
            1: 'Flexible Possession',
            2: 'Deep Build-Up',
            3: 'Long Ball Counter',
            4: 'Dominant Tiki-Taka'
        }
        df['Tactic'] = df['Cluster'].map(cluster_names)
        return df, kmeans_model, scaler
    except Exception as e:
        st.error(f"Clustering error: {str(e)}")
        return df, None, None

@st.cache_data
def train_model(X_train, y_train):
    try:
        model = make_pipeline(
            StandardScaler(),
            SMOTE(random_state=42),
            RandomForestClassifier(
                criterion='gini',
                n_estimators=200,
                max_depth=10,
                class_weight='balanced',
                random_state=33,
                n_jobs=-1
            )
        )
        model.fit(X_train, y_train)
        return model
    except Exception as e:
        st.error(f"Model training error: {str(e)}")
        return None

def main():
    st.title("Football Tactics Classification System with AI")

    # Navigation menu
    selected_page = st.sidebar.selectbox("📂 Select Page", ["🎯 Predict Tactic", "📊 Model Evaluation"])

    df = load_data()
    if df.empty:
        st.warning("No data available. Please check data file path.")
        return

    df = preprocess_data(df)
    df, kmeans_model, scaler = perform_clustering(df)

    if not (kmeans_model and scaler):
        st.error("Clustering failed.")
        return

    X = df.drop(['Cluster', 'Tactic'], axis=1)
    y = df['Tactic']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=44, shuffle=True)
    model = train_model(X_train, y_train)

    # Page 1: Predict Tactic
    if selected_page == "🎯 Predict Tactic":
        with st.sidebar:
            st.header("Match Statistics Input")
            input_data = {}
            for column in X.columns:
                if column not in ['long_passes_percentage', 'shot_accuracy']:
                    input_data[column] = st.number_input(
                        f"Enter {column}:",
                        value=float(X[column].median()),
                        step=0.1,
                        format="%.2f"
                    )

            # Auto-calculate derived values
            if 'long_passes' in input_data and 'total_passes' in input_data:
                if input_data['total_passes'] > 0:
                    input_data['long_passes_percentage'] = (
                        input_data['long_passes'] / input_data['total_passes']
                    ) * 100
                else:
                    st.warning("⚠️ total_passes = 0")
                    input_data['long_passes_percentage'] = 0
                st.markdown(f"**Calculated long_passes_percentage:** {input_data['long_passes_percentage']:.2f}%")

            if 'shots_on_target' in input_data and 'total_shots' in input_data:
                if input_data['total_shots'] > 0:
                    input_data['shot_accuracy'] = (
                        input_data['shots_on_target'] / input_data['total_shots']
                    ) * 100
                else:
                    st.warning("⚠️ total_shots = 0")
                    input_data['shot_accuracy'] = 0
                st.markdown(f"**Calculated shot_accuracy:** {input_data['shot_accuracy']:.2f}%")

            if st.button("Predict Tactic"):
                input_df = pd.DataFrame([input_data])
                input_df = input_df[X.columns]
                prediction = model.predict(input_df)[0]
                st.session_state['prediction'] = prediction
                st.subheader("🔎 Input Summary")
                st.dataframe(input_df)

        if 'prediction' in st.session_state:
            st.subheader("🎯 Predicted Tactic")
            st.success(st.session_state['prediction'])

    # Page 2: Model Evaluation
    elif selected_page == "📊 Model Evaluation":
        st.subheader("📊 Model Evaluation Report")
        y_pred = model.predict(X_test)
        report_dict = classification_report(y_test, y_pred, output_dict=True)
        report_df = pd.DataFrame(report_dict).transpose()
        st.dataframe(report_df.style.format("{:.2f}"))

if __name__ == "__main__":
    main()   