import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

try:
    # Lendo o arquivo CSV com a codificação e o delimitador corretos.
    df = pd.read_csv('tabela_fbes_maximos.csv', delimiter=';', encoding='latin1')
except FileNotFoundError:
    print("Erro: O arquivo 'tabela_fbes_maximos.csv' não foi encontrado.")
    print("Por favor, certifique-se de que ele está na mesma pasta que o script.")
    exit()

# --- Passo 1: Encontrar as Colunas por Conteúdo ---
try:
    # Procura pela coluna de horário e de tipo de camada.
    time_column = [col for col in df.columns if 'horário' in col.lower() or 'horario' in col.lower()][0]
    es_type_column = [col for col in df.columns if 'tipo de camada' in col.lower()][0]
except IndexError:
    print("Erro: Não foi possível encontrar as colunas 'Horário (UT)' ou 'Tipo de camada'.")
    print("Por favor, verifique se os nomes das colunas no seu arquivo estão corretos.")
    exit()

# --- Passo 2: Limpeza e Processamento dos Dados ---

# Convertendo a coluna de tempo.
df[time_column] = df[time_column].str.replace(',', '.', regex=True).astype(float)

# --- Passo 3: Categorização baseada na regra do usuário ---

# Definindo a regra para os horários diurno e noturno.
daytime_start = 6
daytime_end = 18

# Criando a nova coluna 'time_period' para categorizar os dados.
df['time_period'] = df[time_column].apply(
    lambda x: 'Daytime' if daytime_start <= x <= daytime_end else 'Nighttime'
)

# --- Passo 4: Padronização dos nomes dos tipos de camada ---

# Mapeando as letras para os nomes completos.
es_type_mapping = {
    'l': '$Es_l$',
    'f': '$Es_f$',
    'c': '$Es_c$',
    'a': '$Es_a$',
    's': '$Es_s$',
    'h': '$Es_h$'
}

# Aplicando o mapeamento.
df['es_type'] = df[es_type_column].map(es_type_mapping)

# Removendo linhas onde a coluna 'es_type' é nula (NaN) para evitar o TypeError.
df.dropna(subset=['es_type'], inplace=True)

# --- Passo 5: Agrupamento e Cálculo ---

# Obtendo a lista de todos os tipos de camada.
all_es_types = sorted(df['es_type'].unique())

# Agrupando os dados para contar as ocorrências de cada tipo por período.
grouped_data = df.groupby(['time_period', 'es_type']).size().unstack(fill_value=0)

# Calculando o número total de eventos para normalização.
total_daytime_events = (df['time_period'] == 'Daytime').sum()
total_nighttime_events = (df['time_period'] == 'Nighttime').sum()

# Convertendo as contagens para porcentagens.
daytime_percentage = (grouped_data.loc['Daytime'] / total_daytime_events * 100).round(2)
nighttime_percentage = (grouped_data.loc['Nighttime'] / total_nighttime_events * 100).round(2)

# Combinando os dados de porcentagem em um único DataFrame.
final_data = pd.DataFrame({'Daytime': daytime_percentage, 'Nighttime': nighttime_percentage}).fillna(0)
final_data = final_data.reindex(all_es_types, axis=0)

# --- Passo 6: Plotagem do Gráfico ---

# Definindo as posições e a largura das barras.
bar_width = 0.4
x = np.arange(len(final_data.index))

plt.figure(figsize=(10, 7))

# Plotando as barras para o período Diurno e Noturno.
daytime_bars = plt.bar(x - bar_width/2, final_data['Daytime'], bar_width, label=f'Daytime ({total_daytime_events} events)', color='white', edgecolor='black')
nighttime_bars = plt.bar(x + bar_width/2, final_data['Nighttime'], bar_width, label=f'Nighttime ({total_nighttime_events} events)', color='black', edgecolor='black', hatch='//')

# Configurando os rótulos e o título.
plt.ylabel('Ocorrência das camadas E esporádicas (%)', fontsize=12)
plt.xlabel('Tipo de camada E esporádica', fontsize=12)
#plt.title('Ocorrência dos tipos de camadas em horários noturnos e diurnos', fontsize=10)
plt.xticks(x, final_data.index)
plt.legend()
plt.ylim(0, 100) # Garantindo que o eixo Y vá até 100%.

# Adicionando os rótulos de porcentagem em cima das barras.
def add_labels(bars):
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            plt.text(bar.get_x() + bar.get_width() / 2.0, height, f'{height:.1f}%', ha='center', va='bottom', fontsize=8)

# Adicionando rótulos para as barras Diurnas e Noturnas.
add_labels(daytime_bars)
add_labels(nighttime_bars)

plt.tight_layout()

# Salvando o gráfico em um arquivo.
plt.savefig('ocorrencia_camadas_horarios.png')