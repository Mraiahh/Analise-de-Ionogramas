import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# --- Mapeamento das Estações para Títulos ---
FILES_TO_PROCESS = {
    'Solstício de Dezembro': 'arquivo_dezembro.csv',
    'Equinócio de Março': 'arquivo_equinocio_mar.csv',
    'Solstício de Junho': 'arquivo_junho.csv',
    'Equinócio de Setembro': 'arquivo_equinocio_set.csv'
}
# OBS: Altere os nomes dos arquivos acima para os nomes reais dos seus 4 arquivos.
# Vamos assumir que sua coluna de horário se chama 'Hora' ou algo parecido.

def process_and_plot_station(ax, file_path, title):
    """Lê, calcula a porcentagem de ocorrência por hora e plota."""
    
    # --- 1. LEITURA E TRATAMENTO DE ERROS ---
    try:
        # Tenta ler com diferentes codificações
        try:
            df = pd.read_csv(file_path, delimiter=';', encoding='latin1')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, delimiter=';', encoding='cp1252')
            
    except Exception as e:
        print(f"ERRO ao ler {title}: {e}")
        return # Para de processar esta estação
    
    # --- 2. PREPARAÇÃO DA COLUNA DE HORA ---
    df.columns = df.columns.str.strip().str.lower()
    
    try:
        # Busca pela coluna de horário (assumindo que seja 'hora', 'horário', ou 'horario (ut)' )
        hour_column = [col for col in df.columns if 'hora' in col or 'horario' in col][0]
    except IndexError:
        print(f"ERRO: Coluna de horário não encontrada em {title}.")
        return

    # Limpa e converte a coluna de horário (se precisar ser convertida para int para agrupar)
    # Assumindo que a coluna 'Hora' já foi pré-processada para ter apenas o valor da hora (0, 1, ..., 23)
    df[hour_column] = pd.to_numeric(df[hour_column].astype(str).str.split('.').str[0], errors='coerce')
    
    # Remove linhas onde a hora não pôde ser convertida
    df.dropna(subset=[hour_column], inplace=True)
    df[hour_column] = df[hour_column].astype(int)

    # --- 3. CÁLCULO DA OCORRÊNCIA ---
    
    # Conta o total de eventos para normalização
    total_events = len(df)
    
    if total_events == 0:
        print(f"Aviso: {title} não tem eventos válidos.")
        return

    # Agrupa por hora e conta os eventos
    occurrence_counts = df.groupby(hour_column).size()
    
    # Calcula a porcentagem
    occurrence_percentage = (occurrence_counts / total_events) * 100
    
    # Cria uma Série com todas as 24 horas (0 a 23) para garantir que todas as barras apareçam, mesmo com 0 ocorrência
    all_hours = pd.Series(0.0, index=pd.RangeIndex(24))
    final_data = all_hours.add(occurrence_percentage, fill_value=0).sort_index()

    # --- 4. PLOTAGEM ---
    
    hours = final_data.index
    
    # Plota a barra simples
    ax.bar(hours, final_data.values, color='white', edgecolor='black', width=1.0) 
    
    ax.set_title(title, fontsize=12)
    ax.set_ylim(0, 10) # Limite o eixo Y para um valor razoável (ajuste conforme seus dados)
    ax.set_xlim(-0.5, 23.5)
    
    # Formatação do Eixo X: Mostra as horas de 00 a 23
    ax.set_xticks(hours[::2]) # Mostra a cada 2 horas (00, 02, 04...)
    ax.set_xticklabels([f'{h:02d}' for h in hours[::2]])

# -------------------------------------------------------------
## 2. EXECUÇÃO PRINCIPAL E MONTAGEM DA FIGURA
# -------------------------------------------------------------

# Cria a figura e os 4 subplots (2 linhas, 2 colunas)
fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharey=True, sharex=True)
# Achata a matriz de eixos para facilitar a iteração (axes[0,0], axes[0,1], etc. vira uma lista)
axes_flat = axes.flatten()

print("Iniciando o processamento dos arquivos...")

# Itera sobre o dicionário de arquivos e plota em cada subplot
for i, (title, filename) in enumerate(FILES_TO_PROCESS.items()):
    full_path = filename # Se você quiser pedir o caminho ao usuário, integre o loop 'while True' aqui.
    process_and_plot_station(axes_flat[i], full_path, title)

# --- AJUSTES FINAIS DA FIGURA ---

# Rótulos gerais dos eixos
fig.text(0.5, 0.04, 'Hora (UT)', ha='center', fontsize=14)
fig.text(0.04, 0.5, 'Ocorrência dos eventos (%)', va='center', rotation='vertical', fontsize=14)

plt.tight_layout(rect=[0.05, 0.05, 1, 0.95]) # Ajusta o layout e dá espaço para os rótulos
plt.savefig('ocorrencia_sazonal_por_hora.png')
print("\nGráfico 'ocorrencia_sazonal_por_hora.png' salvo com sucesso!")
