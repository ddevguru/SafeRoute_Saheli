import pandas as pd
from sklearn.model_selection import train_test_split

data = pd.read_csv("ml.csv")

X = data[['YearsExperience']]
Y = data['Salary']

X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=0.2, random_state=42
)

print("X_train:")
print(X_train)

print("\nX_test:")
print(X_test)

print("\nY_train:")
print(Y_train)

print("\nY_test:")
print(Y_test)