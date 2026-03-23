# app.py
import streamlit as st
import pandas as pd
import joblib
from dotenv import load_dotenv
import os
import google.generativeai as genai
from quant_model import train_quant_model

# ------------------ CONFIG ------------------
st.set_page_config(
    page_title="Quant + Gemini AI Financial Dashboard",
    layout="wide"
)
load_dotenv()
# Initialize Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model_gemini = genai.GenerativeModel("gemini-2.5-flash-lite")

# ------------------ CUSTOM STYLES ------------------
st.markdown("""
<style>
/* Main background and font */
body, .main, .block-container {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: #f5f5f5;
    font-family: 'Poppins', sans-serif;
}

/* Headings */
h1, h2, h3 {
    text-align: center;
    color: #ffffff;
    font-weight: 700;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(135deg, #1c1c1c, #2a2a2a);
    padding: 20px;
    border-radius: 15px;
}

/* Sidebar headers */
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #00c6ff;
}

/* Input elements */
.stNumberInput>div>div>input, .stSelectbox>div>div>div>div {
    border-radius: 10px;
    padding: 5px;
    background-color: rgba(255,255,255,0.1);
    color: #f5f5f5;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    color: white;
    font-weight: 600;
    border-radius: 10px;
    border: none;
    padding: 0.6em 1.2em;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    transform: scale(1.05);
    background: linear-gradient(90deg, #0072ff, #00c6ff);
}

/* Prediction Card */
.prediction-card {
    background-color: rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 2em;
    margin-top: 1.5em;
    box-shadow: 0 12px 30px rgba(0,0,0,0.4);
    text-align: center;
    transition: all 0.3s ease;
}
.prediction-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.5);
}

/* Gemini Insight styling */
.gemini-insight {
    background-color: rgba(255,255,255,0.06);
    border-left: 5px solid #00c6ff;
    border-radius: 15px;
    padding: 1.5em;
    margin-top: 1em;
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}

/* Footer */
.footer {
    text-align: center;
    color: #c9c9c9;
    margin-top: 50px;
    font-size: 0.9em;
}
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown("<h1> Quant + Gemini AI Hybrid Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:18px;'>AI-powered risk prediction with Gemini-based financial insights</p>", unsafe_allow_html=True)
st.divider()

# ------------------ MODEL TRAINING ------------------
try:
    model, acc, df, target_col = train_quant_model("data/credit_data.csv")
    st.success(f"Model trained successfully — Accuracy: {acc:.2f}")
except Exception as e:
    st.error(f"Error training model: {e}")
    st.stop()

# ------------------ SIDEBAR INPUT ------------------
st.sidebar.header("Customer Data Input")
input_data = {}
for col in df.drop(target_col, axis=1).columns:
    if df[col].dtype == 'object':
        input_data[col] = st.sidebar.selectbox(f"{col}", list(df[col].unique()))
    else:
        input_data[col] = st.sidebar.number_input(f"{col}", value=float(df[col].mean()))

# ------------------ PREDICTION ------------------
if st.sidebar.button("🔮 Predict Default Risk"):
    user_df = pd.DataFrame([input_data])

    # Encode categorical values
    for col in user_df.columns:
        if user_df[col].dtype == 'object':
            user_df[col] = pd.Categorical(user_df[col]).codes

    try:
        prediction = model.predict(user_df)[0]
        prob = model.predict_proba(user_df)[0][1]
        risk_label = "High Risk" if prediction == 1 else "Low Risk"
        color = "#ff4b4b" if prediction == 1 else "#00c851"

        # ------------------ TWO-COLUMN LAYOUT ------------------
        col1, col2 = st.columns(2)

        # Left Column: Prediction Card
        with col1:
            st.markdown(f"""
            <div class="prediction-card">
                <h2 style='color:{color};'>{risk_label}</h2>
                <h3>Probability: {prob:.2f}</h3>
            </div>
            """, unsafe_allow_html=True)

        # Right Column: Gemini AI Insight
        with col2:
            with st.spinner("Gemini analyzing..."):
                prompt = f"""
                You are a financial AI analyst.
                The model predicted this customer's credit default risk as '{risk_label}' with a probability of {prob:.2f}.
                Here’s the customer data: {input_data}.
                Write a concise, data-driven explanation suitable for an internal financial report.
                """
                response = model_gemini.generate_content(prompt)
                ai_text = response.text

                st.markdown("<h3 style='text-align:center;'>Gemini AI Financial Insight</h3>", unsafe_allow_html=True)
                st.markdown(f"<div class='gemini-insight'>{ai_text}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Prediction failed: {e}")

# ------------------ SAVE MODEL ------------------
if st.sidebar.button("💾 Save Model"):
    joblib.dump(model, "quant_model.pkl")
    st.sidebar.success("Model saved as quant_model.pkl")

# ------------------ FOOTER ------------------
st.markdown("""
<div class="footer">
    Built by <b>Sweety</b> | Powered by <b>Gemini AI + Quant Intelligence</b>
</div>
""", unsafe_allow_html=True)
