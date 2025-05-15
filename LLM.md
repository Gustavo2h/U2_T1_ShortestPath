# Processo de Criação do Código com Algoritmos de Roteamento

## Prompt Inicial

Para a criação do código inicial utilizando o algoritmo de **Dijkstra**, foi utilizado o seguinte prompt:

> “Crie um código em Python utilizando o algoritmo de Dijkstra (implemente Dijkstra) e a biblioteca OSMnx para calcular o tempo de resposta de ambulâncias saindo do hospital Walfredo Gurgel em Natal-RN para diferentes bairros de Natal, como Felipe Camarão, Alecrim, Neópolis, Planalto, Pitimbu e Mirassol. A saída deve ser uma tabela com os tempos de resposta e distância do trajeto, tempo de execução do programa e emissão de carbono. Utilize a biblioteca CodeCarbon para avaliar a emissão de carbono da execução. A origem deve ser fixa (hospital), variando os destinos.”

---

## Modificações com Novos Prompts

O código foi então modificado com **prompts simples** para realizar pequenas alterações:

- Para utilizar as funções do próprio OSMnx:

> “Gostaria de uma versão do programa que use as funções do próprio OSMnx para calcular as rotas.”

- Para implementar Dijkstra com Min-Heap:

> “Agora faça uma nova versão utilizando Dijkstra com min-heap a partir do código criado.”

---

## Visualização dos Resultados

Com os códigos criados, corrigidos e testados, foram adicionadas funções da biblioteca **Matplotlib** para plotar os gráficos de visualização das rotas.

---

## Comparação de Desempenho

Por fim, foi utilizado um último prompt, mais simples, para gerar os gráficos de comparação entre os algoritmos em termos de tempo de execução e pegada de carbono:

> “Crie um código em Python que plota um gráfico comparando o tempo de execução de três códigos e a pegada de carbono desses três códigos com os seguintes dados:  
> Dijkstra (tempo = 93.60s , pegada = 0,000298 Kg CO₂),  
> Min-Heap (tempo = 0,07s , pegada = 0,000000 Kg CO₂),  
> OSMnx (tempo = 1,08s , pegada = 0,000004 Kg CO₂).”
