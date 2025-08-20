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
