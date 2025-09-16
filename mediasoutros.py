import pandas as pd
import numpy as np
import os
import re

# --------- CONFIGURE AQUI ----------
entrada = r"C:\ProjetoIonograma\arquivos Louis\FiltroNonC_fbEsAnalysis.xlsx"
saida = os.path.splitext(entrada)[0] + "_medias_corrigido_v2.xlsx"
# Adicione "il" aqui se quiser suportar esse tipo multi-letra
tipos = ["f", "a", "h", "l", "s", "il"]
MAX_OFFSET = 3
NUM_PROP_THRESHOLD = 0.12
TYPE_OCC_THRESHOLD = 3
# -----------------------------------

def extract_types(cell, tipos_set):
    """
    Extrai tokens alfabéticos (sequências de letras) e retorna os tipos
    presentes com base em tipos_set. Suporta tipos multi-letra (ex: 'il')
    e também reconhece letras únicas dentro de tokens se necessário.
    """
    if pd.isna(cell):
        return []
    s = str(cell).lower()
    tokens = re.findall(r'[a-z]+', s)
    found = []
    for tok in tokens:
        # token exato (útil para 'il')
        if tok in tipos_set:
            found.append(tok)
            continue
        # detectar tipos multi-letra como substring (ex: '...il...')
        for typ in tipos_set:
            if len(typ) > 1 and typ in tok and typ not in found:
                found.append(typ)
        # detectar letras únicas dentro do token (compatibilidade com versão anterior)
        for ch in tok:
            if ch in tipos_set and ch not in found:
                found.append(ch)
    return found

# carrega todas as abas
xls = pd.read_excel(entrada, sheet_name=None)
resultados = {}

for sheet_name, df in xls.items():
    print(f"\n=== Processando aba: {sheet_name} ===")
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    # detecta coluna UT (ou LT)
    ut_candidates = [c for c in df.columns if c.strip().lower() in ("ut", "lt")]
    ut_col = ut_candidates[0] if ut_candidates else df.columns[0]
    print("UT detectado:", ut_col)

    tipos_set = set(tipos)

    # 1) Detecta colunas de tipo
    type_cols = []
    type_details = {}
    for c in df.columns:
        extracted = df[c].apply(lambda x: extract_types(x, tipos_set))
        n_valid = extracted.apply(lambda lst: len(lst) > 0).sum()
        counts = {}
        for lst in extracted:
            for t in lst:
                counts[t] = counts.get(t, 0) + 1
        if n_valid >= TYPE_OCC_THRESHOLD and (n_valid / len(df) >= 0.05):
            type_cols.append(c)
            type_details[c] = {"n_valid": n_valid, "counts": counts}
    print("Colunas candidatas a 'tipo':", type_cols)
    if not type_cols:
        type_cols = [c for c in df.columns if re.search(r'\bes\b', c, re.I)]
        print("Fallback: usando colunas com 'Es':", type_cols)

    # 2) Mapeamento type_col -> fb_col (coluna mais próxima numericamente adequada)
    mapping = {}
    for type_col in type_cols:
        col_idx = df.columns.get_loc(type_col)
        fb_col = None

        # tenta a coluna imediatamente à esquerda (sempre preferida se tiver algum número)
        if col_idx > 0:
            candidate = df.columns[col_idx - 1]
            num_series = pd.to_numeric(df[candidate], errors="coerce")
            if num_series.notna().any():
                fb_col = candidate

        # se não encontrou na esquerda, procura em offsets (próximas colunas) respeitando threshold
        if not fb_col:
            offsets = []
            for k in range(1, MAX_OFFSET + 1):
                offsets.extend([k, -k])
            for off in offsets:
                j = col_idx + off
                if 0 <= j < len(df.columns):
                    candidate = df.columns[j]
                    num_series = pd.to_numeric(df[candidate], errors="coerce")
                    prop_num = num_series.notna().mean()
                    if prop_num >= NUM_PROP_THRESHOLD:
                        fb_col = candidate
                        break
        if fb_col:
            mapping[type_col] = fb_col

    # fallback se mapping estiver vazio (tenta colunas com 'fb'/'fbes' no nome)
    if not mapping:
        candidates_fb = [c for c in df.columns if re.search(r'fb', c, re.I) or re.search(r'fbes', c, re.I)]
        if candidates_fb and type_cols:
            for i, c in enumerate(type_cols):
                mapping[c] = candidates_fb[i % len(candidates_fb)]
            print("Fallback forçado usando colunas com 'fb':", mapping)
        else:
            print("ATENÇÃO: não foi possível mapear colunas fb nesta aba automaticamente.")

    # converte as colunas fb mapeadas para numérico
    fb_cols = sorted(set(mapping.values()))
    for fb in fb_cols:
        df[fb] = pd.to_numeric(df[fb], errors="coerce")

    # 3) cálculo linha a linha — IMPORTANTES REGRAS AQUI:
    #   - se o fb_col mapeado estiver NaN naquela linha, IGNORA (não busca outro)
    #   - se duas type_cols apontarem para o mesmo fb_col, conta esse fb_col apenas 1 vez naquela linha
    medias = pd.DataFrame({ut_col: df[ut_col].values})
    counts = pd.DataFrame({ut_col: df[ut_col].values})
    contribs = pd.DataFrame({ut_col: df[ut_col].values})

    for row_idx in df.index:
        for t in tipos:
            vals = []
            contrib_list = []
            seen_fb_cols = set()  # evita duplicar o mesmo fb_col
            for type_col, fb_col in mapping.items():
                t_vals = extract_types(df.at[row_idx, type_col], tipos_set)
                if t in t_vals:
                    # se já usamos este fb_col nesta linha, pula (evita contar 2x)
                    if fb_col in seen_fb_cols:
                        continue
                    v = df.at[row_idx, fb_col]
                    # regra: se v for NaN, IGNORA (não busca outro valor)
                    if pd.notna(v):
                        try:
                            vf = float(v)
                            vals.append(vf)
                            contrib_list.append(f"{type_col}->{fb_col}:{vf}")
                            seen_fb_cols.add(fb_col)
                        except:
                            # se não converter, ignora
                            pass
                    else:
                        # explicitamente ignorado — não procura "ultimo caso" nem faz fill
                        pass
            if vals:
                medias.loc[row_idx, t] = sum(vals) / len(vals)
                counts.loc[row_idx, t + "_count"] = len(vals)
                contribs.loc[row_idx, t + "_contribs"] = ";".join(contrib_list)
            else:
                medias.loc[row_idx, t] = np.nan
                counts.loc[row_idx, t + "_count"] = 0
                contribs.loc[row_idx, t + "_contribs"] = ""

    # debug/resumo
    print("Resumo por tipo (linhas com pelo menos 1 valor):")
    for t in tipos:
        nlines = (counts[t + "_count"] > 0).sum()
        print(f"  {t}: {nlines} linhas")

    # exemplos das primeiras linhas
    n_examples = min(6, len(df))
    print("\nExemplos iniciais (UT | contribs | medias):")
    for i in range(n_examples):
        utv = df.at[df.index[i], ut_col]
        cvals = {t: contribs.at[df.index[i], t + "_contribs"] for t in tipos}
        mvals = {t: medias.at[df.index[i], t] for t in tipos}
        print(f"  UT={utv} -> contribs={cvals} -> medias={mvals}")

    # junta tudo para salvar
    out = pd.concat([
        medias.reset_index(drop=True),
        counts.drop(columns=[ut_col]).reset_index(drop=True),
        contribs.drop(columns=[ut_col]).reset_index(drop=True)
    ], axis=1)

    resultados[sheet_name] = out

# salva
with pd.ExcelWriter(saida) as writer:
    for name, df_out in resultados.items():
        df_out.to_excel(writer, sheet_name=name, index=False)

print("\nArquivo salvo em:", saida)
