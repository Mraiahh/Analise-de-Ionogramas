import pandas as pd

# Carregar o arquivo do Excel no pandas
df = pd.read_excel("C:\ProjetoIonograma\contagemtipos.xlsx")

# Transpor o DataFrame
df_transposto = df.transpose()

# Salvar o novo DataFrame transposto em um novo arquivo Excel
df_transposto.to_excel("C:\ProjetoIonograma\contagemtipos_transposto.xlsx")

