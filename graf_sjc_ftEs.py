import pandas as pd #lê o excel
import numpy as np #faz os cálculos
import matplotlib.pyplot as plt #desenha o gráfico
import matplotlib.gridspec as gridspec #controla o layout dos subplots
from matplotlib.patches import Patch 
from matplotlib.lines import Line2D #montam a legenda

def read_multiblock_sheet(filepath, sheet_name): 
    """Lê uma aba que tem múltiplos blocos de evento,
    cada um com seu próprio cabeçalho de datas.
    Retorna dict: {numero_evento: DataFrame com colunas [LT, data1, data2, ...]}
    """
    df_raw = pd.read_excel(filepath, sheet_name=sheet_name, header=None)

    header_rows = df_raw[df_raw[0] == 'evento'].index.tolist()
    header_rows.append(len(df_raw))

    eventos = {}
    for i, hr in enumerate(header_rows[:-1]):
        next_hr = header_rows[i+1]

        header = df_raw.iloc[hr].tolist() #pega o cabeçalho dessa parte
        date_cols = [c for c in header[2:] if pd.notna(c) and c != '']

        bloco = df_raw.iloc[hr + 1 : next_hr].copy() #pega os dados 
        bloco.columns = range(bloco.shape[1])

        num_evento = bloco[0].iloc[0]

        cols_usar = [1] + list(range(2, 2 + len(date_cols)))
        bloco_limpo = bloco[cols_usar].copy()
        bloco_limpo.columns = ['LT'] + date_cols

        bloco_limpo['LT'] = bloco_limpo['LT'].astype(str).str.replace(',','.').astype(float) #troca a virgula do LT para ponto o convertendo para float

        for dc in date_cols:
            bloco_limpo[dc] = (
                bloco_limpo[dc]
                .astype(str)
                .str.replace(',','.')
                .replace({'-': np.nan, 'nan': np.nan, 'NaN':np.nan})
                .astype(float)
            )
        eventos[int(num_evento)] = bloco_limpo
    
    return eventos

FILEPATH = r"C:\Users\aluno\Downloads\ftes.xlsx" #caminho dos dados

print("Lendo SJC-PERT...")
pert = read_multiblock_sheet(FILEPATH, "SJC-PERT")
print("Lendo SJC-CALM...")
calm = read_multiblock_sheet(FILEPATH, "SJC-CALM")

print("\nEventos encontrados em PERT:", list(pert.keys()))
print("Eventos encontrados em CALM:", list(calm.keys()))

for ev in pert: 
    dias_pert = [c for c in pert[ev].columns if c != 'LT']
    dias_calm = [c for c in calm[ev].columns if c != 'LT']
    print(f"\nEvento {ev}:")
    print(f" Dias PERT: {[str(d.date()) if hasattr(d,'date') else d for d in dias_pert]}")
    print(f" Dias CALM: {[str(d.date()) if hasattr(d,'date') else d for d in dias_calm]}")

#funções auxiliares a partir daqui verificar se n tem outro meio
def lt_to_plot_x(lt_array):
    """Converte LT para começar meia noite """
    lt = np.array(lt_array, dtype=float)
    x = np.where(lt >= 21, lt - 21, lt + 3)
    return x

def tick_labels():
    ticks = [0, 3, 6, 9, 12, 15, 18, 21, 24]
    labels = ['21', '00', '03', '06', '09', '12', '15', '18', '21']
    return ticks, labels

#plotar para um evento 
def plot_evento(num_evento, save=True):
    df_p = pert[num_evento]
    df_c = calm[num_evento]

    dias_pert = [c for c in df_p.columns if c != 'LT']
    dias_calm = [c for c in df_c.columns if c != 'LT']
    n_dias = len(dias_pert)

    #média e desvio padrão dos dias calmos
    calm_vals = df_c[dias_calm].values.astype(float)
    media_calm = np.nanmean(calm_vals, axis=1)
    std_calm = np.nanstd(calm_vals, axis=1) # / np.sqrt(calm_vals.shape[1])

    lt_original = df_p['LT'].values
    lt_plot = (lt_original - 21) % 24 #subtrai 21 e pega o modulo de 24 para virar 00, 01, etc

    largura_quadro = 3.0
    altura_quadro = 4.0
    fig = plt.figure(figsize=(largura_quadro * n_dias, altura_quadro), dpi=100) 

    gs = gridspec.GridSpec(1, n_dias, figure=fig, wspace=0.0) #divide a figura em 1 linha e n colunas 
    ticks, labels = tick_labels()

    for i, dia  in enumerate(dias_pert):
        ax = fig.add_subplot(gs[0, i])

        ax.errorbar(
            lt_plot,
            media_calm,
            yerr=std_calm,
            fmt='-', #linha continua 
            color='gray',
            linewidth=1.2,
            ecolor='darkgray', #cor das barras
            elinewidth=0.7,
            capsize=1.5, #tamanho da pontinha
            #errorevery=3,
            zorder=2,
            label='Médias calmos'
        )

        ax.plot(lt_plot, media_calm, color='gray', linewidth=1.2, label='Média calmos', zorder=2) #linha cinza com a média dos dias perturbados

        vals_pert = df_p[dia].values.astype(float)
        ax.plot(lt_plot, vals_pert, color='red', linewidth=1.0, label='Perturbado', zorder=3) #linha vermelha do dia perturbado

        #formatação!!!!
        data_str = dia.strftime('%d/%m') if hasattr(dia,'strftime') else str(dia)
        ax.set_title(data_str, fontsize=9, pad=3, fontweight='bold')
        ax.set_xlim(0, 24)
        ax.set_ylim(0, 15) #define um valor fixo no topo para todo mundo
        ax.set_xticks(ticks)
        ax.set_xticklabels(labels, fontsize=7)
        ax.grid(True, linestyle='--', alpha=0.4)

        if i==0:
            ax.set_ylabel('ftEs (MHz)', fontsize=9)
            ax.tick_params(axis='y', labelsize=7)
        else:
            ax.tick_params(axis='y', labelleft=False)

    #legenda
    legend_elements = [
        Line2D([0], [0], color='gray', lw=1.5, marker='|', markersize=10, label='Média dos dias calmos'),
        Line2D([0],[0], color='red', lw=1.2, label='Dia Perturbado'),
    ]
    fig.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.95), fontsize=8)

    fig.text(0.5, 0.02, 'Horário Local(LT)', ha='center', fontsize=9, fontweight='bold')

    plt.subplots_adjust(left=0.08, right=0.95, top=0.85, bottom=0.15)

    if save:
        fname=f"ftes_sjc_evento{num_evento}.png"
        plt.savefig(fname, dpi=150, bbox_inches='tight')
        print(f"Salvo: {fname}")
    plt.show()
    plt.close()

# gera os gráficos
for ev in sorted(pert.keys()):
    print(f"\nPlotando evento {ev}...")
    plot_evento(ev, save=True)

print("\nPronto")
