import pandas as pd
import matplotlib.pyplot as plt

# 1. Load the Excel file, skipping the first row of data
# Use `header=1` to get the column names from row 2
# Use `skiprows=2` to skip the first two rows and start reading data from row 3
# Provide the column names explicitly using the `names` parameter
df = pd.read_excel("C:\ProjetoIonograma\contagemtipos_transposto.xlsx", header=None, skiprows=2, names=['Data', 'l', 'f', 'c', 's', 'a', 'h'])

# 2. Convert the 'Data' column to datetime and extract the year
df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
df['Ano'] = df['Data'].dt.year

# 3. Group the data by year and sum the counts of each layer type
# This will sum the numerical columns automatically
dados_agrupados = df.drop('Data', axis=1).groupby('Ano').sum()

# 4. Create the stacked bar chart
fig, ax = plt.subplots(figsize=(10, 6))
dados_agrupados.plot(kind='bar', stacked=True, ax=ax, width=0.8)

# 5. Customize the plot
ax.set_ylabel('Ocorrência de Camadas Es')
ax.set_xlabel('Ano')
ax.set_title('Ocorrência de Camadas Es por Ano')

# Add a legend and adjust the layout
ax.legend(title='Tipo de Es', loc='upper right')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()