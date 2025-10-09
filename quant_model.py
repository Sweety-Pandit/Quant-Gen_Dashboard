# quant_model.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

def train_quant_model(file_path):
    # Load the dataset
    df = pd.read_csv(file_path)

    # Auto-detect target column
    possible_targets = ["default", "delinquency", "target", "risk_flag", "loan_status"]
    target_col = None
    for t in possible_targets:
        if t in df.columns:
            target_col = t
            break

    if not target_col:
        raise ValueError(f"No valid target column found. Expected one of {possible_targets}, but got {list(df.columns)}")

    # Clean dataset
    df = df.dropna()  # Drop rows with NaN values

    # Encode categorical columns
    le = LabelEncoder()
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = le.fit_transform(df[col])

    X = df.drop(target_col, axis=1)
    y = df[target_col]

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    model = LogisticRegression(max_iter=500)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    return model, acc, df, target_col
