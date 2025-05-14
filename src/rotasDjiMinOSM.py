import time
import osmnx as ox
import pandas as pd
from codecarbon import EmissionsTracker
import matplotlib.pyplot as plt
import heapq

# Configurações
weight_attr = 'travel_time'  # peso para otimização
ox.settings.use_cache = True
ox.settings.log_console = False
hospital_address = "Hospital Walfredo Gurgel, Natal, RN, Brazil"
bairro_addresses = {
    "Felipe Camarão": "Felipe Camarão, Natal, RN, Brazil",
    "Alecrim": "Alecrim, Natal, RN, Brazil",
    "Neópolis": "Neópolis, Natal, RN, Brazil",
    "Planalto": "Planalto, Natal, RN, Brazil",
    "Pitimbu": "Pitimbu, Natal, RN, Brazil",
    "Mirassol": "Mirassol, Natal, RN, Brazil"
}

# Geocodificação
hospital_point = ox.geocode(hospital_address)
bairro_points = {b: ox.geocode(addr) for b, addr in bairro_addresses.items()}

# Carregar grafo viário
print("Carregando grafo de Natal...")
g = ox.graph_from_place("Natal, Rio Grande do Norte, Brazil", network_type="drive")
g = ox.add_edge_speeds(g)
g = ox.add_edge_travel_times(g)

# Mapear nós para índices para facilitar lista de adjacência
nodes = list(g.nodes)
idx_of = {node: i for i, node in enumerate(nodes)}
rev_nodes = {i: node for node, i in idx_of.items()}

# Construir lista de adjacência: (vizinho_idx, peso, length)
adj = [[] for _ in nodes]
for u, v, data in g.edges(data=True):
    u_idx, v_idx = idx_of[u], idx_of[v]
    w = data.get(weight_attr, float('inf'))
    l = data.get('length', 0)
    adj[u_idx].append((v_idx, w, l))
    # Grafos de via única; se bidirecional já está duplicado

# Dijkstra com min-heap

def dijkstra_heap(start, end):
    n = len(adj)
    dist = [float('inf')] * n
    prev = [None] * n
    dist[start] = 0
    heap = [(0, start)]  # (dist, vertex)
    while heap:
        d_u, u = heapq.heappop(heap)
        if d_u > dist[u]:
            continue
        if u == end:
            break
        for v, w, _ in adj[u]:
            alt = d_u + w
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                heapq.heappush(heap, (alt, v))
    # reconstruir caminho
    path = []
    u = end
    if prev[u] is not None or u == start:
        while u is not None:
            path.append(u)
            u = prev[u]
        path.reverse()
    return path, dist[end]

# Origem e destinos como índices
o_node = ox.nearest_nodes(g, hospital_point[1], hospital_point[0])
o_idx = idx_of[o_node]
dest_idx = {b: idx_of[ox.nearest_nodes(g, pt[1], pt[0])] for b, pt in bairro_points.items()}

# Iniciar medição de tempo e emissões
tracker = EmissionsTracker()
tracker.start()
start_exec = time.time()

# Calcular rotas
dados = []
routes = {}
for bairro, di in dest_idx.items():
    path_idx, total_wt = dijkstra_heap(o_idx, di)
    routes[bairro] = [rev_nodes[i] for i in path_idx]
    # calcular distância total
    dist_m = 0
    for i in range(len(path_idx) - 1):
        u, v = rev_nodes[path_idx[i]], rev_nodes[path_idx[i+1]]
        dist_m += g[u][v][0].get('length', 0)
    dados.append({
        'Bairro': bairro,
        'Distância (km)': round(dist_m/1000, 2),
        'Tempo de Resposta (min)': round(total_wt/60, 1)
    })

# Finalizar métricas
elapsed = time.time() - start_exec
emissions = tracker.stop()

# Mostrar resultados
df = pd.DataFrame(dados).sort_values('Bairro').reset_index(drop=True)
print(df.to_string(index=False))
print(f"\nTempo de execução: {elapsed:.2f} s")
print(f"Emissão de carbono: {emissions:.6f} kg CO₂")

# Plotagem com legenda e marcação do hospital
fig, ax = ox.plot_graph(
    g,
    figsize=(10, 10),
    bgcolor='white',
    edge_color='dimgray',
    node_size=0,
    show=False,
    close=False
)

# Marcar hospital
hx, hy = g.nodes[o_node]['x'], g.nodes[o_node]['y']

ax.scatter(hx, hy, marker='*', color='red', s=200, label='Hospital')

# Traçar rotas e labels corretos
colors = plt.cm.tab10.colors
for i, (bairro, route) in enumerate(routes.items()):
    # extrair coordenadas da rota
    xs = [g.nodes[n]['x'] for n in route]
    ys = [g.nodes[n]['y'] for n in route]
    ax.plot(xs, ys, color=colors[i % len(colors)], linewidth=3, label=bairro)

# Legenda vinculando bairros e hospital
ax.legend(title='Legenda', loc='lower left', fontsize='small')
ax.set_title('Rotas do Hospital Walfredo Gurgel para bairros de Natal (Min-Heap)')
plt.tight_layout()

# Salvar figura
nome_arquivo = 'Rotas_Min_Heap.png'
fig.savefig(nome_arquivo, dpi=300, bbox_inches='tight')
plt.show()
