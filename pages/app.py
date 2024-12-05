import pandas as pd

df = pd.read_excel('C:/Users/User/Downloads/002.xlsx')
df['CODIGO'] = df['CODIGO'].fillna(0)
df['CODIGO.1'] = df['CODIGO.1'].fillna(0)

set_col1 = set(df['CODIGO'])
set_col2 = set(df['CODIGO.1'])
itens_iguais = set_col1.intersection(set_col2)
itens_unicos_col1 = set_col1 - set_col2
#print(f'Itens em Coluna1 e não em Coluna2: {itens_unicos_col1}')
itens_unicos_col2 = set_col2 - set_col1
#print(f'Itens em Coluna1 e não em Coluna2: {itens_unicos_col2}')
lista_itens_unicos_col1 = list(itens_unicos_col1)
print(f'Itens em CODIGO e não em CODIGO.1: {lista_itens_unicos_col1}')
# Display the cleaned data
df.to_excel("output.xlsx")  
