using System;
using System.IO;
using System.Collections.Generic;

class Programa
{
    static void Teste()
    {
        Console.WriteLine("Digite o caminho completo do arquivo .SJC:");
        string caminhoArquivo = Console.ReadLine();

        if (!File.Exists(caminhoArquivo))
        {
            Console.WriteLine("Arquivo não encontrado.");
            return;
        }

        Dictionary<char, int> contagemTipos = new Dictionary<char, int>
        {
            { 'l', 0 }, { 'f', 0 }, { 'c', 0 },
            { 's', 0 }, { 'a', 0 }, { 'h', 0 }
        };

        try
        {
            string[] linhas = File.ReadAllLines(caminhoArquivo);

            if (linhas.Length < 3)
            {
                Console.WriteLine("Arquivo não tem linhas suficientes para processar.");
                return;
            }

            // A linha do cabeçalho está na terceira linha (índice 2)
            string cabecalho = linhas[2];
            // Assumindo que o arquivo é separado por espaços ou tabulações:
            string[] colunas = cabecalho.Split(new char[] { ' ', '\t' }, StringSplitOptions.RemoveEmptyEntries);

            int indiceEs = Array.IndexOf(colunas, "Es");
            if (indiceEs == -1)
            {
                Console.WriteLine("Coluna 'Es' não encontrada no cabeçalho.");
                return;
            }

            // Agora percorre as linhas seguintes, a partir da linha 4 (índice 3)
            for (int i = 3; i < linhas.Length; i++)
            {
                string[] valores = linhas[i].Split(new char[] { ' ', '\t' }, StringSplitOptions.RemoveEmptyEntries);
                if (valores.Length > indiceEs)
                {
                    char tipo = char.ToLower(valores[indiceEs][0]);
                    if (contagemTipos.ContainsKey(tipo))
                    {
                        contagemTipos[tipo]++;
                    }
                }
            }

            // Mostrar no console
            Console.WriteLine("\nContagem de tipos de camada Es:");
            foreach (var par in contagemTipos)
            {
                Console.WriteLine($"{par.Key}: {par.Value}");
            }

            // Exportar para CSV
            string caminhoCsv = Path.Combine(Path.GetDirectoryName(caminhoArquivo), "resultado_camadas.csv");
            using (StreamWriter sw = new StreamWriter(caminhoCsv))
            {
                sw.WriteLine("Tipo,Contagem");
                foreach (var par in contagemTipos)
                {
                    sw.WriteLine($"{par.Key},{par.Value}");
                }
            }

            Console.WriteLine($"\nArquivo CSV salvo em: {caminhoCsv}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Erro ao processar o arquivo: {ex.Message}");
        }
    }
}
