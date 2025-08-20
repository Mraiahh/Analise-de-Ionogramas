# Projeto-Ionograma
Programas para utilidades específicas da Iniciação Científica

### bloqueio.py
Lê as abas do documento Excel e gera um novo arquivo separando somente as colunas desejadas, nesse caso: 
* Time (fixa no início),
* UT e LT de cada dia
* Es e fbEs três vezes, igual aparece no UDIDA
* Deixa uma coluna vazia no final para separação dos dias 

### filtrocnovo.py
Lê o documento Excel desejado em busca de registros de tipo 'c' na coluna Es e cria dois arquivos com a coluna seguindo a mesma estrutura, porém:
* O primeiro filtra somente o tipo 'c' de camada E esporádica, substituindo todos os registros diferentes e suas respectivas fbEs para 0,
* O segundo filtra todos os tipos diferentes e substitui todos os registros de c e suas respectivas fbEs por 0

### maxfoes.cs
Lê os documentos da redução de dados no formato salvo (pode alterar de acordo com a estação) e gera uma nova tabela com os maiores valores da frequência total encontrados nos arquivos
* Exemplo 
  - arquivo1.SJC
UT LT foEs fbEs
00 01 3.5 2.1
01 02 4.2 2.5
02 03 2.8 1.9
03 04 5.7 3.0
    maior valor: 5.7
- arquivo2.SJC
UT LT foEs fbEs
00 01 1.8 0.9
01 02 2.2 1.0
02 03 2.0 1.1
    maior valor: 2.2
- saída
  Arquivo,Maior_foEs
  arquivo1.SJC,5.70
  arquivo2.SJC,2.20

