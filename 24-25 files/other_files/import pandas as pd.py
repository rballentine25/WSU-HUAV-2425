import pandas as pd
    
data = {'col1': [1, 2, 3], 'col2': ['A', 'B', 'C']}
df = pd.DataFrame(data)
print(df.shape[0])  # Output: (3, 2)
print(df)

