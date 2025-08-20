using System;
using System.IO;
using System.Globalization;
using System.Collections.Generic;

class MaxFoesBatch
{
    static void Teste()
    {
        Console.WriteLine("Digite os caminhos completos dos arquivos .SJC ou .PAL ou .TXT separados por vírgula:");
        string entrada = Console.ReadLine();

        string[] caminhos = entrada.Split(new char[] { ',' }, StringSplitOptions.RemoveEmptyEntries);

        List<string> resultados = new List<string>();
        resultados.Add("Arquivo,Maior_foEs");

        foreach (string caminho in caminhos)
        {
            string caminhoTrimado = caminho.Trim();

            // Verifica se é .SJC ou .PAL
            string extensao = Path.GetExtension(caminhoTrimado).ToLower();
            if (extensao != ".sjc" && extensao != ".pal" && extensao != ".txt")
            {
                Console.WriteLine($"Arquivo ignorado (extensão inválida): {Path.GetFileName(caminhoTrimado)}");
                continue;
            }

            if (!File.Exists(caminhoTrimado))
            {
                Console.WriteLine($"Arquivo não encontrado: {caminhoTrimado}");
                continue;
            }

            try
            {
                string[] linhas = File.ReadAllLines(caminhoTrimado);
                if (linhas.Length < 3)
                {
                    Console.WriteLine($"Arquivo inválido (linhas insuficientes): {Path.GetFileName(caminhoTrimado)}");
                    continue;
                }

                string cabecalho = linhas[2];
                string[] colunas = cabecalho.Split(new char[] { ' ', '\t' }, StringSplitOptions.RemoveEmptyEntries);
                int indicefoEs = Array.IndexOf(colunas, "foEs");

                if (indicefoEs == -1)
                {
                    Console.WriteLine($"Coluna 'foEs' não encontrada: {Path.GetFileName(caminhoTrimado)}");
                    continue;
                }

                double maiorFoEs = double.MinValue;

                for (int i = 3; i < linhas.Length; i++)
                {
                    string[] valores = linhas[i].Split(new char[] { ' ', '\t' }, StringSplitOptions.RemoveEmptyEntries);
                    if (valores.Length > indicefoEs)
                    {
                        string valor = valores[indicefoEs].Replace(',', '.');

                        if (double.TryParse(valor, NumberStyles.Any, CultureInfo.InvariantCulture, out double frequencia))
                        {
                            if (frequencia > maiorFoEs)
                                maiorFoEs = frequencia;
                        }
                    }
                }

                string nomeArquivo = Path.GetFileName(caminhoTrimado);
                if (maiorFoEs == double.MinValue)
                {
                    resultados.Add($"{nomeArquivo},N/A");
                }
                else
                {
                    resultados.Add($"{nomeArquivo},{maiorFoEs.ToString("F2", CultureInfo.InvariantCulture)}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Erro no arquivo {Path.GetFileName(caminhoTrimado)}: {ex.Message}");
            }
        }

        // Salvar CSV
        string caminhoCsv = Path.Combine(Directory.GetCurrentDirectory(), "tabela_maiores5_foEs.csv");
        File.WriteAllLines(caminhoCsv, resultados);

        Console.WriteLine($"\nCSV gerado com sucesso: {caminhoCsv}");
    }
}
