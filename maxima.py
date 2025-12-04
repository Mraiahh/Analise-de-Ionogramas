import pandas as pd

arquivo_entrada = r"C:\Users\aluno\Downloads\SJCWorksheet_08to09.xlsx"
arquivo_saida = r"C:\ProjetoIonograma\SJCWorksheet_foEs.xlsx"

abas = ["SJC-Summer", "SJC-Autumn", "SJC-Winter", "SJC-Spring"]

dados_por_aba = {}

for aba in abas:
    print(f"Processando aba: {aba}")

    df = pd.read_excel(arquivo_entrada, sheet_name=aba, header=[4, 5])
    
    blocos = []
    bloco = 0  

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

                bloco_par.columns = [col[1] if col[1] != "" else col[0] for col in bloco_par.columns]

                pares.append(bloco_par)

            bloco_completo = pd.concat([ut, lt] + pares, axis=1)
            bloco_completo[""] = ""
            blocos.append(bloco_completo.reset_index(drop=True))
            bloco += 1
        except Exception:
            break

    df_final = pd.concat(blocos, axis=1)
    dados_por_aba[aba] = df_final

    print(f"{aba} processada com {bloco} blocos.")

with pd.ExcelWriter(arquivo_saida, engine="openpyxl") as writer:
    for nome, df in dados_por_aba.items():
        df.to_excel(writer, sheet_name=nome, index=False)

print(f"Arquivo salvo em: {arquivo_saida}")

