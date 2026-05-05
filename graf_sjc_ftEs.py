import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D

FILEPATH_PERT = r"C:\Users\aluno\Downloads\ftes.xlsx" #dados perturbados
PATH_BINS = r"C:\Users\aluno\Downloads\calmos" #dados calmos

def read_multiblock_sheet(filepath, sheet_name): 
    df_raw = pd.read_excel(filepath, sheet_name=sheet_name, header=None)
    header_rows = df_raw[df_raw[0] == 'evento'].index.tolist()
    header_rows.append(len(df_raw))

    eventos = {}
    for i, hr in enumerate(header_rows[:-1]):
        next_hr = header_rows[i+1]
        header = df_raw.iloc[hr].tolist()
        date_cols = [c for c in header[2:] if pd.notna(c) and c != '']
        bloco = df_raw.iloc[hr + 1 : next_hr].copy()
        bloco.columns = range(bloco.shape[1])
        num_evento = bloco[0].iloc[0]
        cols_usar = [1] + list(range(2, 2 + len(date_cols)))
        bloco_limpo = bloco[cols_usar].copy()
        bloco_limpo.columns = ['LT'] + date_cols
        bloco_limpo['LT'] = bloco_limpo['LT'].astype(str).str.replace(',','.').astype(float)
        
        for dc in date_cols:
            bloco_limpo[dc] = pd.to_numeric(bloco_limpo[dc].astype(str).str.replace(',','.'), errors='coerce')
        
        eventos[int(num_evento)] = bloco_limpo
    return eventos

print("Lendo SJC-PERT...")
pert = read_multiblock_sheet(FILEPATH_PERT, "SJC-PERT")

def tick_labels():
    ticks = [0, 3, 6, 9, 12, 15, 18, 21, 24]
    labels = ['21', '00', '03', '06', '09', '12', '15', '18', '21']
    return ticks, labels

def plot_evento_com_bins(num_evento, save=True):
    #dados perturbados
    df_p = pert[num_evento]
    dias_pert = [c for c in df_p.columns if c != 'LT']
    n_dias = len(dias_pert)
    
    #carrega os arquivos de dias calmos
    file_bin = f"{PATH_BINS}\\bins_calmos_30min_ev{num_evento}.xlsx"
    try:
        df_referencia = pd.read_excel(file_bin, sheet_name='bins_todos_calmos')
    except Exception as e:
        print(f"Erro ao carregar referência para evento {num_evento}: {e}")
        return

    # converte LT para o gráfico pra deixar tudo junto
    lt_original = df_p['LT'].values
    lt_plot_p = (lt_original - 21) % 24
    
    lt_ref_decimal = df_referencia['LT_decimal'].values
    lt_plot_ref = (lt_ref_decimal - 21) % 24
    
    sort_idx = np.argsort(lt_plot_ref)
    lt_plot_ref = lt_plot_ref[sort_idx]
    media_calm = df_referencia['media_ftes'].values[sort_idx]
    std_calm = df_referencia['std_ftes'].values[sort_idx]

    largura_quadro = 3.5
    altura_quadro = 4.5
    fig = plt.figure(figsize=(largura_quadro * n_dias, altura_quadro), dpi=100)
    gs = gridspec.GridSpec(1, n_dias, figure=fig, wspace=0.1)
    ticks, labels = tick_labels()

    for i, dia in enumerate(dias_pert):
        ax = fig.add_subplot(gs[0, i])

        #plot dos dados dos bins
        ax.errorbar(
            lt_plot_ref, media_calm, yerr=std_calm,
            fmt='-', color='gray', linewidth=1.5,
            ecolor='gray', elinewidth=1, capsize=2,
            alpha=0.7, zorder=2, label='Média Calmos (Bins)'
        )

        #plot dia perturbado
        vals_pert = df_p[dia].values.astype(float)
        ax.plot(lt_plot_p, vals_pert, color='red', linewidth=1.2, zorder=3, label='Dia Perturbado')

        data_str = dia.strftime('%d/%m/%Y') if hasattr(dia,'strftime') else str(dia)
        ax.set_title(f"{data_str}", fontsize=10, fontweight='bold')
        ax.set_xlim(0, 24)
        ax.set_ylim(0, 16) 
        ax.set_xticks(ticks)
        ax.set_xticklabels(labels, fontsize=8)
        ax.grid(True, linestyle=':', alpha=0.6)

        if i == 0:
            ax.set_ylabel('ftEs (MHz)', fontsize=10, fontweight='bold')
        else:
            ax.tick_params(axis='y', labelleft=False)

    # Legenda única
    legend_elements = [
        Line2D([0], [0], color='gray', lw=1.5, label='Média Calmos (Bins 30min)'),
        Line2D([0], [0], color='red', lw=1.2, label='Dia Perturbado'),
    ]
    fig.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 0.98), ncol=2, fontsize=9)
    fig.text(0.5, 0.04, 'Horário Local (LT)', ha='center', fontsize=10, fontweight='bold')

    plt.subplots_adjust(bottom=0.18, top=0.85, left=0.1, right=0.95)

    if save:
        plt.savefig(f"comparativo_ev{num_evento}.png", bbox_inches='tight')
    plt.show()

for ev in sorted(pert.keys()):
    print(f"Gerando gráfico comparativo para Evento {ev}...")
    plot_evento_com_bins(ev)
