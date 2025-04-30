import pandas as pd


file_path = 'C:/Users/rball/OneDrive/Documents/school/24-25 fall/Git Repos f24/WSU-HUAV-2425/24-25 files/9_11_24_Genset_test_3.xlsx'
ard_data = pd.read_excel(file_path, sheet_name='Data1')
print(ard_data.head())