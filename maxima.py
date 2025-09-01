import pandas as pd

# Caminho do arquivo
arquivo_entrada = r"C:\Users\aluno\Downloads\SJCWorksheet_08to09.xlsx"
arquivo_saida = r"C:\ProjetoIonograma\SJCWorksheet_foEs.xlsx"

# Abas com os dados
abas = ["SJC-Summer", "SJC-Autumn", "SJC-Winter", "SJC-Spring"]

# Armazena os DataFrames prontos por aba
dados_por_aba = {}

# Loop pelas abas
for aba in abas:
    print(f"Processando aba: {aba}")
    
    # Lê com cabeçalho nas linhas 5 e 6 (MultiIndex nas colunas)
    df = pd.read_excel(arquivo_entrada, sheet_name=aba, header=[4, 5])
    
    blocos = []
    bloco = 0  # contador de blocos

    while True:
        try:
            # --- Índices UT e LT ---
            ut_idx = 0 + bloco * 18
            lt_idx = ut_idx + 1
            if lt_idx >= df.shape[1]:
                break
            
            ut = df.iloc[:, ut_idx].rename("UT")
            lt = df.iloc[:, lt_idx].rename("LT")
            pares = []

            # Pares de foEs/Es: sempre a partir de ut_idx + 5, saltando 2
            base = ut_idx + 6
            for i in range(3):  # 3 pares por bloco
                fo_idx = base + i * 4
                es_idx = fo_idx + 1
                if es_idx >= df.shape[1]:
                    break

                bloco_par = df.iloc[:, [fo_idx, es_idx]].copy()

                # Preserva os nomes originais do Excel (nível 1 do cabeçalho)
                bloco_par.columns = [col[1] if col[1] != "" else col[0] for col in bloco_par.columns]

                pares.append(bloco_par)

            # Junta UT, LT, pares e separador
            bloco_completo = pd.concat([ut, lt] + pares, axis=1)
            bloco_completo[""] = ""
            blocos.append(bloco_completo.reset_index(drop=True))
            bloco += 1
        except Exception:
            break

    # Junta tudo horizontalmente
    df_final = pd.concat(blocos, axis=1)
    dados_por_aba[aba] = df_final

    print(f"{aba} processada com {bloco} blocos.")

# Salva tudo num único arquivo com várias abas
with pd.ExcelWriter(arquivo_saida, engine="openpyxl") as writer:
    for nome, df in dados_por_aba.items():
        df.to_excel(writer, sheet_name=nome, index=False)

print(f"Arquivo salvo em: {arquivo_saida}")
