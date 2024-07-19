import pandas as pd

df = pd.read_excel('C:/Users/User/Documents/Data Analysis/Projeto_Estoque/Base_dados/Base_dados.xlsx')

# Remove ' 00:00:00' from the 'Data' column
df['ENDERECO'] = df['ENDERECO'].str.replace(' ', '')

# Display the cleaned data
df.to_excel("output.xlsx")  
