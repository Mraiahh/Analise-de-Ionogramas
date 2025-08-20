import pandas as pd

# Caminho do arquivo
arquivo_entrada = r"C:\Users\aluno\Downloads\RealAnalysis5.1.xlsx"
arquivo_saida = r"C:\Users\aluno\ProjetoIonograma\RealAnalysis_Finalof.xlsx"

# Abas com os dados
abas = ["SJC-Summer", "SJC-Autumn", "SJC-Winter", "SJC-Spring"]

# Armazena os DataFrames prontos por aba
dados_por_aba = {}

# Loop pelas abas
for aba in abas:
    print(f"🔄 Processando aba: {aba}")
    
    # Lê com cabeçalho nas linhas 5 e 6
    df = pd.read_excel(arquivo_entrada, sheet_name=aba, header=[4, 5])
    
    # Time (só uma vez)
    coluna_time = df.iloc[:, 0].rename("Time")
    
    blocos = []
    bloco = 0  # contador de blocos

    while True:
        try:
            # Índices UT e LT
            ut_idx = 3 + bloco * 18
            lt_idx = ut_idx + 1
            if lt_idx >= df.shape[1]:
                break
            
            ut = df.iloc[:, ut_idx].rename("UT")
            lt = df.iloc[:, lt_idx].rename("LT")
            pares = []

            # Pares de fbEs/Es: sempre a partir de ut_idx + 5, saltando 2
            base = ut_idx + 5
            for i in range(3):  # 3 pares por bloco
                fb_idx = base + i * 4
                es_idx = fb_idx + 2
                if es_idx >= df.shape[1]:
                    break
                bloco_par = df.iloc[:, [fb_idx, es_idx]].copy()
                bloco_par.columns = [col[1] for col in bloco_par.columns]  # pega só os nomes
                pares.append(bloco_par)

            # Junta UT, LT, pares e separador
            bloco_completo = pd.concat([ut, lt] + pares, axis=1)
            bloco_completo[""] = ""
            blocos.append(bloco_completo.reset_index(drop=True))
            bloco += 1
        except Exception:
            break

    # Junta tudo horizontalmente com a coluna Time
    df_final = pd.concat([coluna_time] + blocos, axis=1)
    dados_por_aba[aba] = df_final
    print(f"✅ {aba} processada com {bloco} blocos.")

# Salva tudo num único arquivo com várias abas
with pd.ExcelWriter(arquivo_saida, engine="openpyxl") as writer:
    for nome, df in dados_por_aba.items():
        df.to_excel(writer, sheet_name=nome, index=False)

print(f"📁 Arquivo salvo em: {arquivo_saida}")
