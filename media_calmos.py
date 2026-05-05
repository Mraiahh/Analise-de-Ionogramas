import pandas as pd
import numpy as np

FILEPATH = r"C:\Users\aluno\Downloads\media calmos_ev4.xlsx"
OUTPUT   = r"C:\Users\aluno\Downloads\bins_calmos_30min_ev4.xlsx"

def ler_aba(filepath, sheet_name):
    """
    Lê uma aba do arquivo de dias calmos.
    Retorna DataFrame com colunas: LT, ftes
    """
    df_raw = pd.read_excel(filepath, sheet_name=sheet_name, header=None)

    #dados começam na linha 4 (índice 4)
    df = df_raw.iloc[4:].copy()
    df.columns = range(df.shape[1])

    # Coluna 1 = LT, Coluna 16 = media ftes
    df = df[[1, 16]].copy()
    df.columns = ['LT', 'ftes']

    df['LT'] = df['LT'].astype(str).str.replace(',', '.').astype(float)

    # ftes: converte para float, zeros viram NaN (zero = sem dado no ionograma)
    df['ftes'] = pd.to_numeric(df['ftes'], errors='coerce')
    df['ftes'] = df['ftes'].replace(0, np.nan)

    df = df.reset_index(drop=True)
    return df

def calcular_bins(df, df_referencia_total=None):
    """
    Recebe DataFrame com colunas LT e ftes.
    Calcula média e desvio padrão em janelas de 30min centradas em
    00:00, 00:30, 01:00, ... 23:30
    Janela: centro ± 15min (ex: bin 00:00 → de 23:45 até 00:15)
    """
    lt = df['LT'].values
    ftes = df['ftes'].values

    dia_atual = df['dia'].iloc[0] if 'dia' in df.columns else None
    # Centros dos bins em horas decimais
    bins_centro = np.arange(0.0, 24.0, 0.5)  # 0.0, 0.5, 1.0, ..., 23.5

    resultados = []

    for centro in bins_centro:
        inicio = centro - 0.25   # -15 min
        fim    = centro + 0.25   # +15 min (exclusive)

        if inicio < 0:
            #tenta pegar os dados do final do dia anterior (se existir)
            try:
                data_atual = pd.to_datetime(dia_atual, dayfirst=True)
                dia_anterior = (data_atual - pd.Timedelta(days=1)).strftime('%d/%m/%Y')

                #verifica se tem o dia anterior
                if df_referencia_total is not None and dia_anterior in df_referencia_total['dia'].values:
                    mask_anterior = (df_referencia_total['dia'] == dia_anterior) & (df_referencia_total['LT'] >= 24 + inicio)
                    valores_antes = df_referencia_total.loc[mask_anterior, 'ftes'].values
                else:
                    #se n tem dia anterior pega as 23:45 do proprio dia
                    mask_proprio_fim = (lt >= 24 + inicio)
                    valores_antes = ftes[mask_proprio_fim]
            except: #caso a conversão de data falhe
                mask_proprio_fim = (lt >= 24 + inicio)
                valores_antes = ftes[mask_proprio_fim]

            #dados do início do dia atual
            mask_depois = (lt < fim)
            valores_depois = ftes[mask_depois]

            valores = np.concatenate([valores_antes, valores_depois])
        
        else:
            #lógica normal para os outros horários
            mask = (lt >= inicio) & (lt < fim)
            valores = ftes[mask]
        
        #limpeza de NaNs 
        valores = valores[~np.isnan(valores)]
        media = np.mean(valores) if len(valores) > 0 else np.nan
        std = np.std(valores) if len(valores) > 0 else np.nan
        n = len(valores)

        hh = int(centro); mm = int(round((centro % 1) * 60))
        label = f"{hh:02d}:{mm:02d}"

        resultados.append({
            'horario': label,
            'LT_decimal': centro,
            'media_ftes': round(media, 4) if not np.isnan(media) else np.nan,
            'std_ftes':   round(std,   4) if not np.isnan(std)   else np.nan,
            'n_pontos':   n
        })

    return pd.DataFrame(resultados)


xl = pd.ExcelFile(FILEPATH)
abas = xl.sheet_names
print(f"Abas encontradas: {abas}")

# Junta todos os dias calmos em um DataFrame único
todos_os_dias = []
for aba in abas:
    print(f"  Lendo aba: {aba}")
    df_dia = ler_aba(FILEPATH, aba)
    df_dia['dia'] = aba  # marca de qual dia veio
    todos_os_dias.append(df_dia)

df_todos = pd.concat(todos_os_dias, ignore_index=True)
print(f"\nTotal de registros lidos: {len(df_todos)}")
print(f"Dias calmos: {df_todos['dia'].unique()}")

#calcula os bins combinando TODOS os dias calmos juntos
df_bins = calcular_bins(df_todos)

print(f"\nPrimeiros bins calculados:")
print(df_bins.head(10).to_string(index=False))

with pd.ExcelWriter(OUTPUT) as writer:
    df_bins.to_excel(writer, sheet_name='bins_todos_calmos', index=False)

    for aba in abas:
        df_dia = ler_aba(FILEPATH, aba)
        df_dia['dia'] = aba
        df_bin_dia = calcular_bins(df_dia,df_referencia_total=df_todos)
        nome_aba = aba.replace('/', '-')[:31]  # Excel limita nome a 31 chars
        df_bin_dia.to_excel(writer, sheet_name=nome_aba, index=False)

print(f"\nArquivo salvo em: {OUTPUT}")
print("Pronto! ✓")
