import pandas as pd

df = pd.read_csv("attendance.csv")
df.to_excel("attendance.xlsx", index=False)

print("Exported to Excel successfully!")
