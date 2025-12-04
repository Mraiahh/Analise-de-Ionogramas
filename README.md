# Projeto-Ionograma
Programas para utilidades específicas da Iniciação Científica

### bloqueio.py
Lê as abas do documento Excel e gera um novo arquivo separando somente as colunas desejadas, nesse caso: 
* Time (fixa no início),
* UT e LT de cada dia
* Es e fbEs três vezes, igual aparece no UDIDA
* Deixa uma coluna vazia no final para separação dos dias 

### maxima.py
Mesma coisa que a de bloqueio, porém ao invés de pegar fbEs, pega a frequência máxima foEs.

### filtrocfbEs.py
Lê o documento Excel desejado em busca de registros de tipo 'c' na coluna Es e cria dois arquivos com a coluna seguindo a mesma estrutura, porém:
* O primeiro filtra somente o tipo 'c' de camada E esporádica, substituindo todos os registros diferentes e suas respectivas fbEs para 0,
* O segundo filtra todos os tipos diferentes e substitui todos os registros de c e suas respectivas fbEs por 0
* o mesmo ocorre com o arquivo **filtrocfoEs.py**, porém este pega as respectivas foEs

### maxfoes.cs
Lê os documentos da redução de dados no formato salvo (pode alterar de acordo com a estação) e gera uma nova tabela com os maiores valores da frequência total encontrados nos arquivos
* Exemplo 
  - arquivo1.SJC
  <img width="118" height="100" alt="image" src="https://github.com/user-attachments/assets/f85e146d-f4f2-49d7-95eb-ba2a3b904a71" />
    maior valor: 5.7
    
  - arquivo2.SJC
  <img width="111" height="81" alt="image" src="https://github.com/user-attachments/assets/614d402f-8351-47ff-b735-edf5ffe204c3" />
    maior valor: 2.2
    
  - saída
  <img width="128" height="63" alt="image" src="https://github.com/user-attachments/assets/99a3734c-6300-402e-8518-e461a517112a" />

### maxfbes.py
Lê os documentos e gera uma nova tabela com o valor máximo da frequência de bloqueio encontrados nos arquivos junto com seu horário em UT

### contadorcamadas.cs
Lê o documento da redução de dados, percorre as colunas Es e conta a quantidade de vezes que cada tipo de camada E esporádica apareceu 

### inverteplanilha.py
Troca as linhas por colunas na planilha 

### graficoporano.py
Faz um gráfico de colunas das ocorrências de camadas E esporádicas divididas por tipo e ano.  
Inspirado no gráfico da Figura 3 no artigo ' Abnormal fb Es enhancements in equatorial Es layers during magnetic storms of solar cycle 23' de L.C.A. Resende, C.M. Denardini, I.S. Batista  
Demonstração do resultado: 
<img width="1154" height="736" alt="image" src="https://github.com/user-attachments/assets/772bb698-2218-42d9-8ad5-9f3df32a1b41" />

### grafdaynight.py
Faz um gráfico de colunas correspondentes ao tipo de camada E esporádica e sua ocorrência dividida em períodos noturnos e diurnos.  
Inspirado no gráfico da Figura 4 no artigo ' Abnormal fb Es enhancements in equatorial Es layers during magnetic storms of solar cycle 23' de L.C.A. Resende, C.M. Denardini, I.S. Batista  
Demonstração do resultado:
<img width="877" height="612" alt="image" src="https://github.com/user-attachments/assets/0e4cb6b5-d882-4eab-a51d-3af1834b6462" />


### mediasoutros.py
Percorre a planilha do Excel (no caso do utilizado, as 4 abas) em busca de registros de letras indicadoras de tipos de camadas E esporádicas e verifica a coluna anterior para pegar o valor da frequência de bloqueio correspondente, calculando a média de ocorrência de cada tipo. 

### grafsazonal.py
Lê os quatro arquivos de cada estação do ano, processa o cálculo e faz o gráfico em barras de ocorrência dos tipos de camada por ano, com cores diferentes para cada tipo.
Inspirado no gráfico da Figura 42  da Tese do Marcelo Henrique Duarte Silva.
Demonstração do resultado:
<img width="1500" height="1200" alt="ocorrencia_anual_sazonal_agrupado_normalizado" src="https://github.com/user-attachments/assets/f0a23669-fdcd-4909-a9f6-1d71d29bdd53" />

### graficofases.py
Percorre as colunas do arquivo inserido e procura pela coluna indicadora da fase da tempestade. Ao encontrar, organiza os dados em duas colunas: a correspondente à fase inicial e principal, e a correspondente à fase de recuperação. 
Inspirado no gráfico da Figura 5 no artigo ' Abnormal fb Es enhancements in equatorial Es layers during magnetic storms of solar cycle 23' de L.C.A. Resende, C.M. Denardini, I.S. Batista  
<img width="2100" height="1800" alt="fbEs_fases_empilhado" src="https://github.com/user-attachments/assets/e2d897a0-02fc-455d-8a9b-ea464ddc4fd0" />

### grafintensidade.py
Percorre as colunas, procura a coluna de intensidade e divide os gráficos em três colunas correspondentes aos níveis fraco, moderado e intenso. 
<img width="2100" height="1800" alt="fbEs_intensidade_empilhado" src="https://github.com/user-attachments/assets/9071ef4d-4ed8-4e77-a41a-a52c2a49a244" />



