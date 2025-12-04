import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import OrderedDict

ES_COLORS = {
    '$Es_l$': '#1f77b4',  # Azul (l)
    '$Es_f$': '#ff7f0e',  # Laranja (f)
    '$Es_c$': '#2ca02c',  # Verde (c)
    '$Es_s$': '#9467bd',  # Roxo (s)
    '$Es_a$': '#8c564b',  # Marrom (a) 
    '$Es_h$': '#d62728',  # Vermelho (h)
}

ES_TYPE_COLUMNS = ['f', 'l', 'c', 's', 'a', 'h']

STATION_NAMES = [
    'Verão',
    'Equinócio de Outono (Março)',
    'Inverno (Solstício de Junho)',
    'Equinócio de Primavera (Setembro)',
]


FILES_TO_PROCESS = OrderedDict()
print("Por favor, insira o caminho completo dos 4 arquivos Excel (.xlsx).")
print("Separe os caminhos por PONTO-E-VÍRGULA (;) na SEGUINTE ORDEM:")
print("1. Verão | 2. Outono | 3. Inverno | 4. Primavera")

while True:
    user_input = input("Caminhos dos 4 arquivos (separados por ';'): ")
    
    file_paths = user_input.split(';')
    
    file_paths = [p.strip() for p in file_paths if p.strip()]
    
    if len(file_paths) != len(STATION_NAMES):
        print(f"\nERRO: Você inseriu {len(file_paths)} caminhos. Precisamos de exatamente {len(STATION_NAMES)}.")
        continue
    
    all_files_exist = True
    for path in file_paths:
        if not os.path.exists(path):
            print(f"ERRO: Arquivo não encontrado no caminho: {path}")
            all_files_exist = False
            break
        if not path.lower().endswith('.xlsx'):
            print(f"ERRO: O arquivo '{path}' não parece ser um arquivo Excel (.xlsx).")
            all_files_exist = False
            break
            
    if all_files_exist:
        FILES_TO_PROCESS = OrderedDict(zip(STATION_NAMES, file_paths))
        print("\nArquivos verificados e prontos para processamento.")
        break
    else:
        continue

# função de processamento e plotagem

def process_and_plot_grouped(ax, file_path, title, es_colors, es_type_cols):
    """Lê, calcula a taxa de ocorrência (% do total do ano) e plota o gráfico agrupado."""
    
    try:
        df = pd.read_excel(file_path, header=0) 
            
    except Exception as e:
        print(f"ERRO FATAL ao ler {title} em {file_path}: {e}")
        return None, None 

    df.columns = df.columns.str.strip().str.lower()
    
    try:
        date_column = [col for col in df.columns if 'data ssc' in col or 'data' in col][0]
        
        if not all(col in df.columns for col in es_type_cols):
            missing = [col for col in es_type_cols if col not in df.columns]
            raise IndexError(f"Erro: As colunas de tipo de camada ({missing}) não foram encontradas.")
            
    except IndexError as e:
        print(f"Erro no cabeçalho em {title}: {e}")
        return None, None

    for col in es_type_cols:
         df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.', regex=True), errors='coerce').fillna(0)

    df['Ano'] = pd.to_datetime(df[date_column], errors='coerce', dayfirst=True).dt.year
    df['Ano'] = df['Ano'].astype('Int64')
    df.dropna(subset=['Ano'], inplace=True)

    df_long = pd.melt(
        df,
        id_vars=['Ano'],
        value_vars=es_type_cols,
        var_name='es_type_code',
        value_name='Contagem'
    )
    
    es_type_mapping = {
        'l': '$Es_l$', 'f': '$Es_f$', 'c': '$Es_c$',
        'a': '$Es_a$', 's': '$Es_s$', 'h': '$Es_h$'
    }
    df_long['es_type'] = df_long['es_type_code'].map(es_type_mapping)
    
    df_long = df_long[df_long['Contagem'] > 0].dropna(subset=['es_type'])
    
    counts = df_long.groupby(['Ano', 'es_type'])['Contagem'].sum().unstack(fill_value=0)
    total_per_year = counts.sum(axis=1)
    
    if total_per_year.empty or (total_per_year == 0).all():
        print(f"Aviso: Não há dados válidos para plotagem em {title}.")
        return None, None
        
    occurrence_percentage = (counts.div(total_per_year, axis=0) * 100).fillna(0)
    
    all_es_types = list(es_colors.keys())
    data_to_plot = occurrence_percentage.reindex(columns=all_es_types, fill_value=0)
    
    num_types = len(all_es_types) 
    bar_width = 0.8 / num_types 
    
    x = np.arange(len(data_to_plot.index)) # Posição de cada ano
    
    legend_handles = []
 
    for i, es_type in enumerate(all_es_types):
        color = es_colors.get(es_type, 'grey')
        values = data_to_plot[es_type]
        
        pos = x + (i - (num_types - 1) / 2) * bar_width
        
        bar = ax.bar(
            pos,
            values,
            width=bar_width,
            label=es_type,
            color=color,
            edgecolor='black'
        )
        legend_handles.append(bar)
        
    ax.set_title(title, fontsize=12)
    ax.set_ylim(0, 100) # O limite Y é fixo em 100%, pois os dados são porcentagens
    ax.set_xticks(x)
    ax.set_xticklabels(data_to_plot.index.astype(str), rotation=45, ha='right')
    
    return legend_handles, all_es_types

fig, axes = plt.subplots(2, 2, figsize=(15, 12), sharey=True) 
axes_flat = axes.flatten()

print("\nProcessando arquivos...")

all_handles = []
all_labels = []

for i, ((title, filename), ax) in enumerate(zip(FILES_TO_PROCESS.items(), axes_flat)):
    print(f"-> Processando estação: {title}")
    
    handles, labels = process_and_plot_grouped(ax, filename, title, ES_COLORS, ES_TYPE_COLUMNS)

    if handles is not None:
        if not all_handles:
            all_handles = handles
            all_labels = labels

if all_handles:
    fig.legend(
        all_handles, 
        all_labels, 
        loc='upper center', 
        bbox_to_anchor=(0.5, 0.98), 
        ncol=len(all_labels),
        title='Tipos de Camadas Es',
        frameon=False,
        fontsize=10
    )

fig.text(0.5, 0.04, 'Ano de Ocorrência', ha='center', fontsize=16)
fig.text(0.04, 0.5, 'Taxa de Ocorrência do Tipo de Camada (%)', va='center', rotation='vertical', fontsize=16)

plt.tight_layout(rect=[0.05, 0.05, 1, 0.9]) 
plt.savefig('ocorrencia_anual_sazonal_agrupado_normalizado.png')
print("\nGráfico final 'ocorrencia_anual_sazonal_agrupado_normalizado.png' salvo com sucesso!")
