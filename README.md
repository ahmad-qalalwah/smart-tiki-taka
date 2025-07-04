# Smart Tiki-Taka ⚽️📊

**Smart Tiki-Taka** is an AI-powered football analytics system designed to support coaches and analysts in making tactical decisions based on real match data. The system transforms raw football data into actionable insights through various modules, combining machine learning, data visualization, and statistical modeling.

---

## 🚀 Features

### 📌 1. Match Shot Analysis
- Visualizes all shots taken in a match with xG (Expected Goals).
- Helps identify dangerous zones and evaluate shooting efficiency.
- **Data Source:** StatsBomb API

### 📌 2. Passing Analysis
- Displays team passing networks and player connections.
- Analyzes pass accuracy and key distributors in the match.
- **Data Source:** StatsBomb API

### 📌 3. Top Scorer Analysis
- Predicts top scorers using xG, shot volume, and accuracy.
- Compares player offensive performance throughout the tournament.
- **Data Source:** StatsBomb API

### 📌 4. Formation Analysis
- Suggests optimal formations to counter an opponent's setup.
- Trained on real match data and formations.
- **Data Source:** FBref (using `pandas.read_html`)

### 📌 5. Tactical Pattern Classification
- Automatically classifies a team’s playing style (e.g., Tiki-Taka, High Press).
- Combines K-Means clustering and Random Forest classification.
- **Data Source:** StatsBomb API (stored in CSV)

---

## 🧠 Technologies Used
- Python  
- Streamlit  
- Scikit-learn  
- Pandas  
- MplSoccer

---

## 📚 Data Sources
- **StatsBomb API**: For match events, shots, passes, xG data  
- **FBref**: For team formations and statistical tables (scraped via pandas)
