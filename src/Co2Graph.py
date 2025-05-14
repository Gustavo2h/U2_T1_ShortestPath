import matplotlib.pyplot as plt

# Dados
algoritmos = ["Djikstra", "Min-Heap", "OSMnx"]
tempo_execucao = [93.60, 0.07, 1.08]  # Tempo em segundos
pegada_carbono = [0.000298, 0.000000, 0.000004]  # Pegada de carbono em Kg CO2

# Criando o primeiro gráfico - Tempo de Execução
plt.figure(figsize=(8,5))
plt.bar(algoritmos, tempo_execucao, color='royalblue')
plt.xlabel("Algoritmos")
plt.ylabel("Tempo de Execução (s)")
plt.title("Tempo de Execução dos Algoritmos")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

# Criando o segundo gráfico - Pegada de Carbono
plt.figure(figsize=(8,5))
plt.bar(algoritmos, pegada_carbono, color='darkorange')
plt.xlabel("Algoritmos")
plt.ylabel("Pegada de Carbono (Kg CO2)")
plt.title("Pegada de Carbono dos Algoritmos")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()
