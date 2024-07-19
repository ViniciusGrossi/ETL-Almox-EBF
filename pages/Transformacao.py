import streamlit as st
import pandas as pd
from io import BytesIO

# Função para processar o arquivo do ERP
def process_file(uploaded_file):
    # Ler o arquivo Excel
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    
    # Verificar as primeiras linhas para entender a estrutura
    st.write("Primeiras linhas do DataFrame original:")
    st.write(df.head())
    
    # Mover os valores da coluna 'QUANTIDADE' 3 posições para cima
    df['QUANTIDADE'] = df['C.A.'].shift(-3)
    
    # Remover linhas em branco na coluna 'CODIGO'
    df = df.dropna(subset=['CODIGO'])
    
    # Remover linhas onde 'CODIGO' começa com '0'
    df = df[~df['CODIGO'].astype(str).str.startswith('0')]

    # Criar coluna 'CODIGO' com valores que começam com '5' e têm exatamente 12 dígitos na coluna 'A'
    df['CODIGO'] = df['CODIGO'].astype(str).str.replace(r'\s0$', '', regex=True)
    df['CÓDIGO'] = df['CODIGO'].astype(str).str.extract(r'(\b5\d{11}\b)')
    df_codigo = df.dropna(subset=['CÓDIGO'])
    
    # Remover duplicatas na coluna 'CODIGO'
    df_codigo = df_codigo.drop_duplicates(subset=['CÓDIGO'])

    # Criar coluna 'DESCRICAO' com valores da coluna 'B'
    df_codigo['DESCRICAO'] = df_codigo['DESCRICAO'].str.strip()
    df_codigo = df_codigo[df_codigo['DESCRICAO'] != '']
    df_codigo = df_codigo.dropna(subset=['DESCRICAO'])

    # Criar coluna 'ENDERECO' com valores que seguem a estrutura específica na coluna 'A'
    df['ENDERECO'] = df['CODIGO'].astype(str)
    df_endereco = df[~df['ENDERECO'].str.startswith(('E', 'N', '5'), na=False)]
    df_endereco['ENDERECO'] = df_endereco['ENDERECO'].str.replace(' 0,00000', '')

    # Garantir que ambos os DataFrames têm o mesmo índice para permitir a junção correta
    df_codigo = df_codigo.reset_index(drop=True)
    df_endereco = df_endereco.reset_index(drop=True)

    # Juntar os DataFrames resultantes
    df_resultado = pd.concat([df_codigo, df_endereco[['ENDERECO']]], axis=1)

    # Selecionar apenas as colunas relevantes
    df_resultado = df_resultado[['CODIGO', 'DESCRICAO', 'ENDERECO', 'QUANTIDADE']]
    
    return df_resultado

# Função para ajustar a base de dados original com a atualização de quantidades
def adjust_quantities(base_file, update_file):
    if base_file is not None and update_file is not None:
        df_base = pd.read_excel(base_file, engine='openpyxl')
        df_update = pd.read_excel(update_file, engine='openpyxl')
        
        st.write("Primeiras linhas da base de dados original:")
        st.write(df_base.head())
        st.write("Primeiras linhas do arquivo de atualização:")
        st.write(df_update.head())

        # Garantir que a coluna 'DESCRICAO' está no formato correto e não tem duplicatas
        df_base['DESCRICAO'] = df_base['DESCRICAO'].astype(str).str.replace(r'\.0+$', '', regex=True)
        df_update['DESCRICAO'] = df_update['DESCRICAO'].astype(str).str.replace(r'\.0+$', '', regex=True)
        df_update = df_update.drop_duplicates(subset=['DESCRICAO'])
        
        # Criar um dicionário de atualização de quantidades
        update_dict = df_update.set_index('DESCRICAO')['QUANTIDADE'].to_dict()
        
        # Substituir os valores de 'QUANTIDADE' na base original com base nos valores do arquivo de atualização
        df_base['QUANTIDADE'] = df_base['DESCRICAO'].map(update_dict).fillna(df_base['QUANTIDADE'])
        st.write("Após atualizar a coluna 'QUANTIDADE':")
        st.write(df_base.head())
    
    return df_base

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

def main():
    st.title("Sistema de Limpeza e Transformação de Dados")

    # Criação de abas
    tab1, tab2 = st.tabs(["Transformação", "Ajuste de Base de Dados"])

    with tab1:
        st.header("Transformação")
        uploaded_file = st.file_uploader("Escolha um arquivo Excel do ERP", type="xlsx")
        if uploaded_file is not None:
            df_resultado = process_file(uploaded_file)
            
            st.write("Dados Processados:")
            st.write(df_resultado)
            
            processed_data = to_excel(df_resultado)
            
            # Baixar o arquivo processado
            st.download_button(
                label="Baixar Arquivo Processado",
                data=processed_data,
                file_name="dados_processados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with tab2:
        st.header("Ajuste de Base de Dados")
        base_file = st.file_uploader("Escolha um arquivo Excel da base de dados original", type="xlsx")
        update_file = st.file_uploader("Escolha o arquivo Excel de atualização (transformado)", type="xlsx")
        if base_file is not None and update_file is not None:
            df_resultado = adjust_quantities(base_file, update_file)
            
            adjusted_data = to_excel(df_resultado)
            
            # Baixar o arquivo ajustado
            st.download_button(
                label="Baixar Arquivo Ajustado",
                data=adjusted_data,
                file_name="dados_ajustados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()