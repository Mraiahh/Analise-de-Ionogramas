import pandas as pd
import numpy as np
import re

file_name = r"C:\ProjetoIonograma\SJCWorksheet_fbEs.xlsx"

try:
    excel_file = pd.ExcelFile(file_name)
    sheet_names = excel_file.sheet_names

    # --- Arquivo "FiltroC" (mantém 'c', o resto vira 0) ---
    with pd.ExcelWriter("FiltroC_Analysis.xlsx", engine="openpyxl", mode="w") as writer_filtered:
        for sheet in sheet_names:
            print(f"🔄 Processando aba '{sheet}' para FiltroC...")
            df = excel_file.parse(sheet, header=0)
            
            # Limpa os nomes das colunas de forma dinâmica, removendo espaços e tratando o ponto
            new_columns = [re.sub(r'\s*\.\s*', '.', col).strip() for col in df.columns.astype(str)]
            df.columns = new_columns

            filtered_df = df.copy()

            # Encontra todas as colunas Es e fbEs de forma dinâmica
            es_cols = sorted([col for col in filtered_df.columns if col.startswith('Es.') or col == 'Es'])
            fbes_cols = sorted([col for col in filtered_df.columns if col.startswith('fbEs.') or col == 'fbEs'])
            
            # Garante que os pares estão corretos e na mesma ordem
            # A lógica é baseada na ideia de que para cada 'Es.N' existe um 'fbEs.N' correspondente
            if len(es_cols) == len(fbes_cols):
                dynamic_col_map = dict(zip(es_cols, fbes_cols))
                
                print(f"✅ Pares de colunas encontrados para esta aba: {dynamic_col_map}")
                
                for es_col, fbes_col in dynamic_col_map.items():
                    filtered_df[es_col] = filtered_df[es_col].astype(str).str.strip().str.lower()
                    filtered_df[fbes_col] = pd.to_numeric(filtered_df[fbes_col], errors='coerce').fillna(0)
                    
                    condition = filtered_df[es_col] != 'c'
                    
                    filtered_df[es_col] = np.where(condition, '0', filtered_df[es_col])
                    filtered_df[fbes_col] = np.where(condition, 0, filtered_df[fbes_col])
            else:
                print("Atenção: Número de colunas Es e fbEs não correspondem nesta aba. Pulando o filtro.")
            
            filtered_df.to_excel(writer_filtered, sheet_name=sheet, index=False)

    # --- Arquivo "FiltroNaoC" (mantém o que não é 'c', só o 'c' vira 0) ---
    with pd.ExcelWriter("FiltroNaoC_Analysis.xlsx", engine="openpyxl", mode="w") as writer_replaced:
        for sheet in sheet_names:
            print(f"\nProcessando aba '{sheet}' para FiltroNaoC...")
            df = excel_file.parse(sheet, header=0)
            
            # Limpa os nomes das colunas de forma dinâmica
            new_columns = [re.sub(r'\s*\.\s*', '.', col).strip() for col in df.columns.astype(str)]
            df.columns = new_columns
            
            replaced_df = df.copy()

            # Encontra todas as colunas Es e fbEs de forma dinâmica
            es_cols = sorted([col for col in replaced_df.columns if col.startswith('Es.') or col == 'Es'])
            fbes_cols = sorted([col for col in replaced_df.columns if col.startswith('fbEs.') or col == 'fbEs'])
            
            if len(es_cols) == len(fbes_cols):
                dynamic_col_map = dict(zip(es_cols, fbes_cols))
                
                print(f"Pares de colunas encontrados para esta aba: {dynamic_col_map}")

                for es_col, fbes_col in dynamic_col_map.items():
                    replaced_df[es_col] = replaced_df[es_col].astype(str).str.strip().str.lower()
                    replaced_df[fbes_col] = pd.to_numeric(replaced_df[fbes_col], errors='coerce').fillna(0)

                    condition = replaced_df[es_col] == 'c'

                    replaced_df[es_col] = np.where(condition, '0', replaced_df[es_col])
                    replaced_df[fbes_col] = np.where(condition, 0, replaced_df[fbes_col])
            else:
                print("Atenção: Número de colunas Es e fbEs não correspondem nesta aba. Pulando o filtro.")

            replaced_df.to_excel(writer_replaced, sheet_name=sheet, index=False)

except FileNotFoundError:
    print(f"Erro: O arquivo '{file_name}' não foi encontrado.")
except Exception as e:
    print(f"Erro inesperado: {e}")

print("\nProcessamento concluído. Verifique os novos arquivos Excel.")
