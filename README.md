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
  <img width="118" height="100" alt="image" src="https://github.com/user-attachments/assets/f85e146d-f4f2-49d7-95eb-ba2a3b904a71" />
    maior valor: 5.7
    
  - arquivo2.SJC
  <img width="111" height="81" alt="image" src="https://github.com/user-attachments/assets/614d402f-8351-47ff-b735-edf5ffe204c3" />
    maior valor: 2.2
    
  - saída
  Arquivo,Maior_foEs
  arquivo1.SJC,5.70
  arquivo2.SJC,2.20

