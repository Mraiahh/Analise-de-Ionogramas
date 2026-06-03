"""
plot_kp_dst.py
==============
Gera gráfico de Kp (barras vermelhas) e Dst (linha preta) a partir de
arquivos .txt no formato dos exemplos fornecidos.
 
Uso:
    python plot_kp_dst.py
 
Configurações no bloco CONFIG abaixo:
    - DST_FILE  : caminho para o arquivo de Dst
    - KP_FILE   : caminho para o arquivo de Kp
    - OUTPUT    : nome do arquivo de saída (PNG, PDF, etc.)
    - EVENT_LABEL: label do evento para o título (opcional)
"""
 
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime, timedelta
 
# ──────────────────────────────────────────────────────────────────────────────
# CONFIG — edite aqui para cada novo evento
# ──────────────────────────────────────────────────────────────────────────────
DST_FILE    = "dst_ev1.txt"   # arquivo de Dst horário
KP_FILE     = "kp_ev1.txt"   # arquivo de Kp (formato NOAA/GFZ diário)
OUTPUT      = "kp_dst_plot.png"
EVENT_LABEL = "Evento 1"      # usado no título (pode deixar vazio "")
DPI         = 150
# ──────────────────────────────────────────────────────────────────────────────
 
 
# ─── LEITURA DO DST ───────────────────────────────────────────────────────────
def load_dst(path):
    """
    Espera colunas: DATE  TIME  DOY  DST
    Ex.: 2016-09-25  00:00:00.000  269  -10.00
    """
    df = pd.read_csv(
        path,
        delim_whitespace=True,
        names=["DATE", "TIME", "DOY", "DST"],
        skiprows=1,          # pula cabeçalho
        parse_dates={"DATETIME": ["DATE", "TIME"]},
    )
    df["DATETIME"] = pd.to_datetime(df["DATETIME"], format="%Y-%m-%d %H:%M:%S.%f",
                                    errors="coerce")
    df = df.dropna(subset=["DATETIME"]).sort_values("DATETIME").reset_index(drop=True)
    df["DST"] = pd.to_numeric(df["DST"], errors="coerce")
    return df
 
 
# ─── LEITURA DO KP ────────────────────────────────────────────────────────────
def parse_kp_value(s):
    """Converte '4+' → 4.33, '3-' → 2.67, '4' → 4.0"""
    s = str(s).strip()
    if s.endswith("+"):
        return float(s[:-1]) + 1/3
    elif s.endswith("-"):
        return float(s[:-1]) - 1/3
    else:
        try:
            return float(s)
        except ValueError:
            return np.nan
 
 
def load_kp(path):
    """
    Espera formato NOAA/GFZ:
    YYYYMMDD  Kp[8] (8 valores de 3h)  Sum  ap[8] (8 valores)  Ap
    Ex.: 20160925  4  4+1  4-3-3  4+4+27+  27  32  4  22  12  15  32  32  22
    """
    rows = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("Y"):   # pula cabeçalho
                continue
            parts = line.split()
            if len(parts) < 9:
                continue
            date_str = parts[0]                    # YYYYMMDD
            # Os 8 valores de Kp estão nas posições 1..8
            kp_strs = parts[1:9]
            try:
                date = datetime.strptime(date_str, "%Y%m%d")
            except ValueError:
                continue
            for i, ks in enumerate(kp_strs):
                dt = date + timedelta(hours=i * 3)
                kp_val = parse_kp_value(ks)
                rows.append({"DATETIME": dt, "KP": kp_val, "KP_STR": ks})
    df = pd.DataFrame(rows).sort_values("DATETIME").reset_index(drop=True)
    return df
 
 
# ─── DAILY Kp SUM ─────────────────────────────────────────────────────────────
def daily_kp_sum(kp_df):
    """Retorna dict {date: sum_str} para labels no topo do gráfico."""
    kp_df = kp_df.copy()
    kp_df["DATE"] = kp_df["DATETIME"].dt.date
    summary = {}
    for date, grp in kp_df.groupby("DATE"):
        total = grp["KP"].sum()
        # mantém sinal do arredondamento mais próximo
        rounded = int(round(total))
        summary[date] = str(rounded)
    return summary
 
 
# ─── PLOT ─────────────────────────────────────────────────────────────────────
def plot(dst_df, kp_df, output=OUTPUT, event_label=EVENT_LABEL, dpi=DPI):
    fig, ax1 = plt.subplots(figsize=(14, 3.5))
    ax1.set_facecolor("white")
    fig.patch.set_facecolor("white")
 
    # ── Barras de Kp (eixo esquerdo) ──────────────────────────────────────────
    bar_width_days = 3 / 24        # 3 horas em fração de dia
    bar_times = kp_df["DATETIME"]
    bar_vals  = kp_df["KP"]
 
    ax1.bar(
        bar_times,
        bar_vals,
        width=timedelta(hours=2.8),
        color="red",
        edgecolor="darkred",
        linewidth=0.3,
        zorder=2,
        label="$k_p$",
        align="edge",
    )
 
    ax1.set_ylabel("$k_p$", fontsize=11)
    ax1.set_ylim(0, 9)
    ax1.set_yticks(range(0, 10))
    ax1.tick_params(axis="y", labelsize=9)
 
    # ── Linha do Dst (eixo direito) ────────────────────────────────────────────
    ax2 = ax1.twinx()
    ax2.plot(
        dst_df["DATETIME"],
        dst_df["DST"],
        color="black",
        linewidth=1.2,
        label="Dst",
        zorder=3,
    )
    ax2.set_ylabel("Dst (nT)", fontsize=11)
    # limites dinâmicos com margem
    dst_min = dst_df["DST"].min()
    dst_max = dst_df["DST"].max()
    margin = max(10, abs(dst_min) * 0.1)
    ax2.set_ylim(dst_min - margin, dst_max + margin)
    ax2.tick_params(axis="y", labelsize=9)
 
    # ── Eixo X: horas (00, 06, 12, 18) por dia ───────────────────────────────
    start = kp_df["DATETIME"].min().normalize()
    end   = dst_df["DATETIME"].max()
 
    ticks = []
    t = start
    while t <= end + timedelta(hours=1):
        ticks.append(t)
        t += timedelta(hours=6)
 
    ax1.set_xlim(start, end + timedelta(hours=3))
    ax1.set_xticks(ticks)
    ax1.set_xticklabels(
        [d.strftime("%H") for d in ticks],
        fontsize=8,
    )
    ax1.tick_params(axis="x", which="both", length=4)
 
    # ── Linhas verticais separando dias ───────────────────────────────────────
    day = start + timedelta(days=1)
    while day <= end:
        ax1.axvline(day, color="gray", linewidth=0.5, linestyle="--", zorder=1, alpha=0.5)
        day += timedelta(days=1)
 
    # ── Labels de dias e daily Kp sum no topo ────────────────────────────────
    daily_sums = daily_kp_sum(kp_df)
    unique_days = sorted(set(kp_df["DATETIME"].dt.date))
    for d in unique_days:
        day_start = datetime.combine(d, datetime.min.time())
        day_mid   = day_start + timedelta(hours=12)
        ksum = daily_sums.get(d, "?")
        ax1.text(
            day_mid, 8.4,
            f"daily $k_p$ = {ksum}",
            ha="center", va="bottom", fontsize=7.5, color="black",
        )
 
    # ── Legenda ───────────────────────────────────────────────────────────────
    kp_patch  = mpatches.Patch(color="red",  label="$k_p$")
    dst_line  = plt.Line2D([0], [0], color="black", linewidth=1.2, label="Dst")
 
    # Legenda em cada sub-painel de dia (como na figura original)
    # Simplificado: legenda única no canto superior esquerdo
    ax1.legend(
        handles=[kp_patch, dst_line],
        loc="upper left",
        fontsize=8,
        framealpha=0.7,
        handlelength=1.2,
    )
 
    # ── Título (opcional) ─────────────────────────────────────────────────────
    if event_label:
        ax1.set_title(event_label, fontsize=10, loc="left", pad=4)
 
    plt.tight_layout()
    fig.savefig(output, dpi=dpi, bbox_inches="tight")
    print(f"Gráfico salvo em: {output}")
    plt.close(fig)
 
 
# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Carregando Dst...")
    dst_df = load_dst(DST_FILE)
    print(f"  {len(dst_df)} linhas de Dst | {dst_df['DATETIME'].min()} → {dst_df['DATETIME'].max()}")
 
    print("Carregando Kp...")
    kp_df = load_kp(KP_FILE)
    print(f"  {len(kp_df)} intervalos de Kp | {kp_df['DATETIME'].min()} → {kp_df['DATETIME'].max()}")
 
    print("Plotando...")
    plot(dst_df, kp_df, output=OUTPUT, event_label=EVENT_LABEL)
