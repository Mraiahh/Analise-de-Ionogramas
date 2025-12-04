import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import unicodedata
import sys

ES_COLORS = {
    'l': '#1f77b4',
    'f': '#ff7f0e',
    'c': '#2ca02c',
    's': '#9467bd',
    'a': '#8c564b',
    'h': '#d62728',
}
ES_TYPES = ['l', 'f', 'c', 's', 'a', 'h']

file_path = input("Digite o caminho do arquivo (CSV ou XLSX): ").strip()
if not os.path.exists(file_path):
    print("Arquivo não encontrado:", file_path)
    sys.exit(1)

#função utilitária
def normalize_text(s):
    if pd.isna(s):
        return s
    s = str(s).strip().lower()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    return s

ext = os.path.splitext(file_path)[1].lower()

if ext in ['.xls', '.xlsx']:
    df = pd.read_excel(file_path)

elif ext == '.csv':
    # tenta várias codificações e separadores AUTOMATICAMENTE
    tried = False
    for enc in ['utf-8', 'latin-1', 'windows-1252']:
        for sep in [';', ',', '\t']:
            try:
                df = pd.read_csv(file_path, encoding=enc, sep=sep, engine='python')
                tried = True
                break
            except Exception:
                continue
        if tried:
            break
    if not tried:
        raise ValueError("Não foi possível ler o CSV. Tente salvar como UTF-8 no Excel.")

else:
    raise ValueError("Formato não suportado. Use CSV ou XLSX.")

df.columns = df.columns.str.strip().str.lower()
df.columns = [normalize_text(c) for c in df.columns]

phase_cols = [c for c in df.columns if 'fase' in c]
if not phase_cols:
    raise ValueError("Coluna de fase da tempestade não encontrada.")
phase_col = phase_cols[0]

existing = set(df.columns)
ES_present = []
for t in ES_TYPES:
    if t in existing:
        ES_present.append(t)
    else:
        df[t] = 0  # cria se faltar
        ES_present.append(t)

for t in ES_present:
    df[t] = df[t].astype(str).str.replace(',', '.', regex=False)
    df[t] = pd.to_numeric(df[t], errors='coerce').fillna(0)

df[phase_col] = df[phase_col].apply(normalize_text)

phase_map = {
    'precedente': 'inicial_principal',
    'preceding phase': 'inicial_principal',
    'main phase': 'inicial_principal',
    'principal': 'inicial_principal',
    'recuperacao': 'recuperação',
    'recuperacao ': 'recuperação',
    'recuperacaoo': 'recuperação',
    'recovery phase': 'recuperação',
}
df['fase_padrao'] = df[phase_col].map(lambda x: phase_map.get(x, x))

phase_order = [ 'inicial_principal', 'recuperação']

#cálculo das frequências
results = {}
for phase in phase_order:
    subset = df[df['fase_padrao'] == phase]

    total = subset[ES_TYPES].sum().sum()

    if total == 0:
        results[phase] = {t: 0.0 for t in ES_TYPES}
    else:
        results[phase] = {t: (subset[t].sum() / total) * 100 for t in ES_TYPES}

plot_df = pd.DataFrame(results).T.fillna(0)[ES_TYPES]

#plot do gráfico
fig, ax = plt.subplots(figsize=(7, 6))

bottom = np.zeros(len(plot_df))
x = np.arange(len(plot_df.index))

for t in ES_TYPES:
    vals = plot_df[t].values
    ax.bar(x, vals, bottom=bottom, color=ES_COLORS[t], edgecolor='black', label=t)
    bottom += vals

ax.set_xticks(x)
ax.set_xticklabels(['Fase Inicial + Principal', 'Fase de Recuperação'], fontsize=11)
ax.set_ylabel('Taxa de Ocorrência do Tipo de Camada (%)', fontsize=12)
ax.set_ylim(0, 100)
#ax.grid(axis='y', linestyle='--', linewidth=0.6, alpha=0.7)

# legenda horizontal fora do gráfico
ax.legend(
    loc='upper center',            # Posição de ancoragem da legenda (no centro acima do ponto de ancoragem)
    bbox_to_anchor=(0.5, -0.15),  # Coordenadas (x, y) relativas ao eixo. 0.5 é o centro, -0.15 é abaixo do eixo X.
    ncol=6,                        # Número de colunas para organizar a legenda (opcional, pode ser 2 ou 3)
    frameon=True,
    edgecolor='black',
    title='Es types'
)

plt.tight_layout()
plt.savefig("fbEs_fases_empilhado.png", dpi=300)
print("Gráfico salvo como fbEs_fases_empilhado.png")
plt.show()
