import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib

# Sample dataset
data = {
    "income": [30000, 45000, 50000, 25000, 70000, 80000],
    "loan_amount": [1000000, 2000000, 1500000, 3000000, 2500000, 2000000],
    "approved": [0, 1, 1, 0, 1, 1]
}

df = pd.DataFrame(data)

X = df[["income", "loan_amount"]]
y = df["approved"]

model = DecisionTreeClassifier()
model.fit(X, y)

joblib.dump(model, "loan_model.pkl")

print("Model Saved Successfully!")