import pandas as pd
import streamlit as st
from io import BytesIO
from datetime import datetime

st.set_page_config('Consulta Estoque', layout='wide')

# Carregar o arquivo Excel
df = pd.read_excel('Base_dados.xlsx')

df['ENDERECO'] = df['ENDERECO'].astype(str).str.strip()
df['CODIGO'] = df['CODIGO'].astype(str)
descricoes = df['DESCRICAO'].unique().tolist()
codigos = df['CODIGO'].unique().tolist()
referencias = df['REFERENCIA'].unique().tolist()
 
# ---------------Sidebar--------------------
show_all_items = st.sidebar.toggle('Pesquisar por Endereço')

if show_all_items:
    corredor = st.sidebar.selectbox('Qual corredor você quer ver?', ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12'])
    modulo = st.sidebar.selectbox('Qual módulo você quer ver?', ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10', 'M11', 'M12', 'M13', 'M14', 'M15', 'M16', 'M17', 'M18', 'M19', 'M20', 'M21', 'M22', 'M23', 'M24', 'M25', 'M26', 'M27', 'M28'])
    nivel = st.sidebar.selectbox('Qual nível você quer ver?', ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 'N9'])
else:
    corredor = ''
    modulo = ''
    nivel = ''

# ---------------Layout--------------------
tab1, tab2, tab3 = st.tabs(['Home', 'Inconsistências', 'Relatório'])

if 'inconsistencias' not in st.session_state:
    st.session_state.inconsistencias = pd.DataFrame(columns=['Item_Selecionado', 'Descricao', 'Codigo', 'Tipo_Inconsistencia', 'Valor_Correto'])

with tab1:
    search_term = st.selectbox('Pesquisar por Descrição, Código ou Referência', [''] + descricoes + codigos + referencias, index=0)
    search_term_lower = str(search_term).lower()

    # Filtrar pelo termo de pesquisa em minúsculas
    df_filtered = df[(df['DESCRICAO'].str.lower().str.contains(search_term_lower, na=False)) | 
                     (df['CODIGO'].str.lower().str.contains(search_term_lower, na=False)) |
                     (df['REFERENCIA'].str.lower().str.contains(search_term_lower, na=False))]

    # Aplicar filtros específicos
    if corredor:
        df_filtered = df_filtered[df_filtered['ENDERECO'].str.startswith(corredor)]
    if modulo:
        df_filtered = df_filtered[df_filtered['ENDERECO'].str.contains(modulo, na=False)]
    if nivel:
        df_filtered = df_filtered[df_filtered['ENDERECO'].str.contains(nivel, na=False)]

    df_filtered.index = df_filtered.index.astype(str).str.replace(',', '')
    df_filtered = df_filtered[df_filtered['ENDERECO'].str.match(f'{corredor}[^0-9]')]
    df_filtered = df_filtered[df_filtered['ENDERECO'].str.match(f'{corredor}{modulo}[^0-9]')]

    if 'Item_Completo' in df_filtered.columns:  # Verificar se a coluna 'Item_Completo' está presente
        df_filtered = df_filtered.drop(columns=['Item_Completo'])  # Remover a coluna 'Item_Completo'

    # Transformar o DataFrame em um data editor
    df_editor = st.data_editor(df_filtered)

    remaining_items = df.copy()
    selected_indices = st.multiselect('Selecione os itens que quer separar', remaining_items.index, placeholder='Um item por vez...')

    # Remover os itens selecionados do DataFrame 'remaining_items'
    remaining_items = remaining_items.drop(selected_indices, errors='ignore')
    st.warning("Após salvar as alterações de inconsistência, lembre-se de excluir o item.")
selected_items = pd.DataFrame()



with tab2:
    st.header('Inconsistências')
    if selected_indices:
        selected_rows = df.loc[selected_indices]
        selected_items = pd.concat([selected_items, selected_rows])
        st.write("Item Selecionado:")
        st.dataframe(selected_items)

        # Adicionar um selectbox para selecionar o tipo de inconsistência
        tipo_inconsistencia = st.selectbox('Selecione o tipo de inconsistência', ['Quantidade', 'Endereço'], index=0)

        # Adicionar um campo para inserir o valor correto
        if tipo_inconsistencia == 'Quantidade':
            valor_correto = st.number_input('Digite o valor correto', step=1)
        elif tipo_inconsistencia == 'Endereço':
            endereco_correto = st.text_input('Digite o endereço correto', max_chars= 10)

        # Botão para salvar a inconsistência
        if st.button('Salvar Inconsistência'):
            if tipo_inconsistencia == 'Quantidade':
                if valor_correto:
                    nova_inconsistencia = pd.DataFrame({
                        'Item_Selecionado': [selected_indices],
                        'Descricao': [selected_rows.iloc[0]['DESCRICAO']],
                        'Cód Marca': [selected_rows.iloc[0]['COD MARCA']],
                        'U.N': [selected_rows.iloc[0]['U.N']],
                        'Codigo': [selected_rows.iloc[0]['CODIGO']],
                        'Tipo_Inconsistencia': [tipo_inconsistencia],
                        'Valor_Correto': [int(valor_correto)]
                    })
                    st.session_state.inconsistencias = pd.concat([st.session_state.inconsistencias, nova_inconsistencia], ignore_index=True)
                    st.success('Inconsistência salva com sucesso!')
                else:
                    st.warning('Por favor, insira um valor numérico.')
            elif tipo_inconsistencia == 'Endereço':
                if endereco_correto:
                    nova_inconsistencia = pd.DataFrame({
                        'Item_Selecionado': [selected_indices],
                        'Descricao': [selected_rows.iloc[0]['DESCRICAO']],
                        'Codigo': [selected_rows.iloc[0]['CODIGO']],
                        'Tipo_Inconsistencia': [tipo_inconsistencia],
                        'Endereço_Correto': [endereco_correto]
                    })
                    st.session_state.inconsistencias = pd.concat([st.session_state.inconsistencias, nova_inconsistencia], ignore_index=True)
                    st.success('Inconsistência salva com sucesso!')
                else:
                    st.warning('Por favor, insira um endereço válido.')

with tab3:
    st.header('Relatório de Inconsistências')
    if not st.session_state.inconsistencias.empty:
        st.dataframe(st.session_state.inconsistencias)
        file_name = st.text_input('Digite o nome do arquivo')
        if st.button('Exportar para Excel'):
            buffer = BytesIO()
            st.session_state.inconsistencias.to_excel(buffer, index=False, engine='openpyxl')
            buffer.seek(0)
            current_date = datetime.now().strftime('%Y-%m-%d')
            full_file_name = f"{file_name}_{current_date}.xlsx"
            st.download_button(
                label="Baixar arquivo Excel",
                data=buffer,
                file_name=full_file_name,
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    else:
        st.write('Nenhuma inconsistência registrada!')
        