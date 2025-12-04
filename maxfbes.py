import os
import sys

def Teste():
    """
    Processa arquivos .SJC, .PAL ou .TXT para encontrar o maior valor de 'fbEs'
    e o valor 'UT' correspondente, salvando os resultados em um arquivo CSV.
    """
    print("Digite os caminhos completos dos arquivos .SJC, .PAL ou .TXT separados por vírgula:")
    entrada = input()

    caminhos = [caminho.strip() for caminho in entrada.split(',') if caminho.strip()]

    resultados = []

    resultados.append("Arquivo,Maior_fbEs,UT_Correspondente,tipo_Es")

    for caminho_trimado in caminhos:

        extensao = os.path.splitext(caminho_trimado)[1].lower()
        if extensao not in ['.sjc', '.pal', '.txt']:
            print(f"Arquivo ignorado (extensão inválida): {os.path.basename(caminho_trimado)}")
            continue

        if not os.path.exists(caminho_trimado):
            print(f"Arquivo não encontrado: {caminho_trimado}")
            continue

        try:
            with open(caminho_trimado, 'r', encoding='utf-8') as arquivo:
                linhas = arquivo.readlines()

            if len(linhas) < 3:
                print(f"Arquivo inválido (linhas insuficientes): {os.path.basename(caminho_trimado)}")
                continue

            cabecalho = linhas[2].strip()
            colunas = cabecalho.split()

            try:
                indice_fbes = colunas.index("fbEs")
                indice_ut = colunas.index("UT")
                indice_tipo = colunas.index("Es")
            except ValueError:
                # O erro não indica qual coluna está faltando, então vamos ser mais específicos.
                if "fbEs" not in colunas:
                    print(f"Erro: Coluna 'fbEs' não encontrada em {os.path.basename(caminho_trimado)}")
                if "UT" not in colunas:
                    print(f"Erro: Coluna 'UT' não encontrada em {os.path.basename(caminho_trimado)}")
                if "Es" not in colunas:
                    print(f"Erro: Coluna 'Es' não encontrada em {os.path.basename(caminho_trimado)}")
                continue

            maior_fbes = -float('inf')
            ut_correspondente = "N/A"
            tipo_correspondente = "N/A"

            for i in range(3, len(linhas)):
                valores = linhas[i].strip().split()
                
                if len(valores) > indice_fbes and len(valores) > indice_ut and len(valores) > indice_tipo:
                    valor_fbes_str = valores[indice_fbes].replace(',', '.')
                    
                    try:
                        frequencia = float(valor_fbes_str)
                        if frequencia > maior_fbes:
                            maior_fbes = frequencia
                            ut_correspondente = valores[indice_ut]
                            tipo_correspondente = valores[indice_tipo] # Linha corrigida
                    except ValueError:
                        pass

            nome_arquivo = os.path.basename(caminho_trimado)
            if maior_fbes == -float('inf'):
                resultados.append(f"{nome_arquivo},N/A,N/A,N/A")
            else:
                resultados.append(f"{nome_arquivo},{maior_fbes:.2f},{ut_correspondente},{tipo_correspondente}")

        except Exception as ex:
            print(f"Erro no arquivo {os.path.basename(caminho_trimado)}: {ex}")

    caminho_csv = os.path.join(os.getcwd(), "tabela_fbes_maximos4.csv")
    with open(caminho_csv, 'w', encoding='utf-8') as f:
        f.write('\n'.join(resultados))

    print(f"\nCSV gerado com sucesso: {caminho_csv}")

if __name__ == "__main__":

    Teste()
