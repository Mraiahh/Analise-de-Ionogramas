import pandas as pd
import os

# Defina o caminho completo para o seu arquivo Excel
file_name = "C:/Users/aluno/Downloads/RealAnalysis_Finalof.xlsx"

# Colunas de interesse para o processamento
es_cols = ['Es', 'Es.1', 'Es.2']
fbes_cols = ['fbEs', 'fbEs.1', 'fbEs.2']

try:
    # Lê o arquivo Excel, e vamos processar cada aba separadamente
    # A função read_excel pode ler todas as abas de uma vez
    excel_file = pd.ExcelFile(file_name)
    sheet_names = excel_file.sheet_names

    # Cria um escritor para cada arquivo Excel de saída
    with pd.ExcelWriter("Filtered_Analysis.xlsx") as writer_filtered, \
         pd.ExcelWriter("Replaced_Analysis.xlsx") as writer_replaced:
        
        # Loop através de cada aba do arquivo
        for sheet in sheet_names:
            # Lê a aba com o cabeçalho na linha correta
            df = excel_file.parse(sheet, header=5)
            df.columns = df.columns.str.strip()

            print(f"Processando a aba: {sheet}")
            
            # Converte as colunas de interesse para o tipo "objeto" (string)
            # Isso evita o aviso FutureWarning
            for col in es_cols + fbes_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str)

            # --- Passo 1: Criar o DataFrame filtrado (sem substituições) ---
            
            # Copia apenas as linhas onde 'c' está presente em 'Es', 'Es.1' ou 'Es.2'
            filtered_df = df[(df['Es'] == 'c') | (df['Es.1'] == 'c') | (df['Es.2'] == 'c')].copy()

            # Salva a aba filtrada no arquivo Excel de saída
            filtered_df.to_excel(writer_filtered, sheet_name=sheet, index=False)
            
            # --- Passo 2: Criar o DataFrame com substituições no conjunto de dados completo ---

            # Cria uma cópia do DataFrame original para aplicar as substituições
            replaced_df = df.copy()

            # Para cada par de colunas (Es, fbEs), se o valor na coluna Es for 'c',
            # substitui o valor de ambas as colunas por '0'
            for es_col, fbes_col in zip(es_cols, fbes_cols):
                condition = replaced_df[es_col] == 'c'
                replaced_df.loc[condition, [es_col, fbes_col]] = '0'

            # Salva a aba substituída no arquivo Excel de saída
            replaced_df.to_excel(writer_replaced, sheet_name=sheet, index=False)
            
except FileNotFoundError:
    print(f"Erro: O arquivo '{file_name}' não foi encontrado.")
except Exception as e:
    print(f"Ocorreu um erro ao processar o arquivo: {e}")

print("Processamento concluído. Verifique os novos arquivos Excel em sua pasta.")