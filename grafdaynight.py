import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

while True:

    file_path = input("Por favor, digite o caminho completo (incluindo o nome e a extensão .csv) do arquivo: ")
    
    if not os.path.exists(file_path):
        print(f"Erro: O arquivo '{file_path}' não foi encontrado.")
        print("Tente novamente e certifique-se de que o caminho está correto.")
        continue 
        
    try:
        df = pd.read_csv(file_path, delimiter=';', encoding='latin1')
        print(f"Arquivo '{file_path}' lido com sucesso.")
        break 
        
    except UnicodeDecodeError:
        print("Erro de Codificação: Não foi possível ler o arquivo com 'latin1'. Tentando com 'cp1252'...")
        try:
            df = pd.read_csv(file_path, delimiter=';', encoding='cp1252')
            print("Leitura bem-sucedida usando 'cp1252'.")
            break
        except Exception as e:
            print(f"Erro: Não foi possível ler o arquivo com 'latin1' ou 'cp1252'. Detalhe: {e}")
            print("Por favor, verifique a codificação do seu arquivo e tente novamente.")
            
    except Exception as e:
        print(f"Ocorreu um erro ao tentar ler o arquivo: {e}")
        print("Verifique se o arquivo é um CSV válido com ';' como delimitador.")


df.columns = df.columns.str.strip().str.lower()

try:
    time_column = [col for col in df.columns if 'horário' in col or 'horario' in col][0]
    es_type_column = [col for col in df.columns if 'tipo de camada' in col][0]
except IndexError:
    print("Erro: Não foi possível encontrar as colunas 'Horário (UT)' ou 'Tipo de camada'.")
    print("Por favor, verifique se os nomes das colunas no seu arquivo estão corretos.")
    exit()

df[time_column] = df[time_column].str.replace(',', '.', regex=True).astype(float)

daytime_start = 9
daytime_end = 21

df['time_period'] = df[time_column].apply(
    lambda x: 'Daytime' if daytime_start <= x <= daytime_end else 'Nighttime'
)

es_type_mapping = {
    'l': '$Es_l$',
    'f': '$Es_f$',
    'c': '$Es_c$',
    'a': '$Es_a$',
    's': '$Es_s$',
    'h': '$Es_h$'
}

df['es_type'] = df[es_type_column].map(es_type_mapping)

df.dropna(subset=['es_type'], inplace=True)

all_es_types = sorted(df['es_type'].unique())

grouped_data = df.groupby(['time_period', 'es_type']).size().unstack(fill_value=0)

total_daytime_events = (df['time_period'] == 'Daytime').sum()
total_nighttime_events = (df['time_period'] == 'Nighttime').sum()

daytime_percentage = (grouped_data.loc['Daytime'] / total_daytime_events * 100).round(2)
nighttime_percentage = (grouped_data.loc['Nighttime'] / total_nighttime_events * 100).round(2)

final_data = pd.DataFrame({'Daytime': daytime_percentage, 'Nighttime': nighttime_percentage}).fillna(0)
final_data = final_data.reindex(all_es_types, axis=0)

bar_width = 0.4
x = np.arange(len(final_data.index))

plt.figure(figsize=(10, 7))

daytime_bars = plt.bar(x - bar_width/2, final_data['Daytime'], bar_width, label=f'Diurnos ({total_daytime_events} eventos)', color='white', edgecolor='black')
nighttime_bars = plt.bar(x + bar_width/2, final_data['Nighttime'], bar_width, label=f'Noturnos ({total_nighttime_events} eventos)', color='black', edgecolor='black', hatch='//')

plt.ylabel('Ocorrência das camadas E esporádicas (%)', fontsize=12)
plt.xlabel('Tipo de camada E esporádica', fontsize=12)
#plt.title('Ocorrência dos tipos de camadas em horários noturnos e diurnos', fontsize=10)
plt.xticks(x, final_data.index)
plt.legend()
plt.ylim(0, 100) # eixo y vai até 100%

def add_labels(bars):
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            plt.text(bar.get_x() + bar.get_width() / 2.0, height, f'{height:.1f}%', ha='center', va='bottom', fontsize=8)

add_labels(daytime_bars)
add_labels(nighttime_bars)

plt.tight_layout()

# Salva o gráfico 
plt.savefig('ocorrencia_horarios.png')
