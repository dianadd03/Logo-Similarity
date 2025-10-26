import pandas as pd

df = pd.read_parquet("logos.snappy.parquet")

print("Forma tabelului (rânduri, coloane):", df.shape)
print("\nColoane disponibile:")
print(df.columns.tolist())

print("\nPrimele 5 rânduri:")
print(df.head(5))
