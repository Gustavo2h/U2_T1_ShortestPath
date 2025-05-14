import time
import osmnx as ox
import pandas as pd
from codecarbon import EmissionsTracker
import matplotlib.pyplot as plt

# 1) Configurações OSMnx
ox.settings.use_cache = True
ox.settings.log_console = False

# 2) Peso para otimização
weight_attr = 'travel_time'

# 3) Endereços
hospital_address = "Hospital Walfredo Gurgel, Natal, RN, Brazil"
bairro_addresses = {
    "Felipe Camarão": "Felipe Camarão, Natal, RN, Brazil",
    "Alecrim":        "Alecrim, Natal, RN, Brazil",
    "Neópolis":       "Neópolis, Natal, RN, Brazil",
    "Planalto":       "Planalto, Natal, RN, Brazil",
    "Pitimbu":        "Pitimbu, Natal, RN, Brazil",
    "Mirassol":       "Mirassol, Natal, RN, Brazil"
}

# 4) Geocodificação
hospital_point = ox.geocode(hospital_address)
bairro_points  = {b: ox.geocode(addr) for b, addr in bairro_addresses.items()}

# 5) Carregar grafo de direção e adicionar atributos
g = ox.graph_from_place(
    "Natal, Rio Grande do Norte, Brazil",
    network_type="drive"
)
g = ox.add_edge_speeds(g)
g = ox.add_edge_travel_times(g)

# 6) Mapear nós para índices para lista de adjacência
nodes    = list(g.nodes)
idx_of   = {node: i for i, node in enumerate(nodes)}
rev_nodes= {i: node for node, i in idx_of.items()}

# 7) Construir lista de adjacência: (v, peso_ travel_time, length)
adj = [[] for _ in nodes]
for u, v, data in g.edges(data=True):
    ui = idx_of[u]; vi = idx_of[v]
    w  = data.get(weight_attr, float('inf'))
    l  = data.get('length', 0)
    adj[ui].append((vi, w, l))

# 8) Implementação de Dijkstra simples (O(V²+E))
def dijkstra_simple(start, end):
    n     = len(adj)
    dist  = [float('inf')] * n
    prev  = [None] * n
    seen  = [False] * n
    dist[start] = 0

    for _ in range(n):
        # encontre o não visto de menor distância
        u = min(
            (i for i in range(n) if not seen[i]),
            key=lambda i: dist[i],
            default=None
        )
        if u is None or dist[u] == float('inf'):
            break
        if u == end:
            break
        seen[u] = True
        for v, w, _ in adj[u]:
            if seen[v]: 
                continue
            alt = dist[u] + w
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u

    # reconstruir caminho
    path = []
    u = end
    if prev[u] is not None or u == start:
        while u is not None:
            path.append(u)
            u = prev[u]
        path.reverse()
    return path, dist[end]

# 9) Origem e destinos em índices
orig_node = ox.nearest_nodes(
    g, hospital_point[1], hospital_point[0]
)
o_idx = idx_of[orig_node]
dest_idx = {
    b: idx_of[ox.nearest_nodes(g, pt[1], pt[0])]
    for b, pt in bairro_points.items()
}

# 10) Medir tempo de execução e emissões
tracker = EmissionsTracker()
tracker.start()
t0 = time.time()

# 11) Calcular rotas, distâncias e tempos
results = []
routes  = {}
for bairro, di in dest_idx.items():
    path_idx, total_wt = dijkstra_simple(o_idx, di)
    route_nodes = [rev_nodes[i] for i in path_idx]
    routes[bairro] = route_nodes

    # somar length e travel_time
    dist_m = 0; time_s = 0
    for u_i, v_i in zip(path_idx[:-1], path_idx[1:]):
        u = rev_nodes[u_i]; v = rev_nodes[v_i]
        data = g.get_edge_data(u, v)
        attrs= data[next(iter(data))]
        dist_m += attrs.get('length', 0)
        time_s += attrs.get(weight_attr, 0)

    results.append({
        'Bairro': bairro,
        'Distância (km)': round(dist_m/1000, 2),
        'Tempo de Resposta (min)': round(time_s/60, 1)
    })

elapsed   = time.time() - t0
emissions = tracker.stop()

# 12) Exibir tabela
df = pd.DataFrame(results).sort_values('Bairro').reset_index(drop=True)
print(df.to_string(index=False))
print(f"\nTempo de execução: {elapsed:.2f} s")
print(f"Emissão de carbono: {emissions:.6f} kg CO₂")

# 13) Plot — grafo base + rotas + hospital + legenda
fig, ax = ox.plot_graph(
    g,
    figsize=(10, 10),
    bgcolor='white',
    edge_color='dimgray',
    node_size=0,
    show=False,
    close=False
)

# marcar hospital
hx = g.nodes[orig_node]['x']; hy = g.nodes[orig_node]['y']
ax.scatter(hx, hy, marker='*', color='red', s=200, label='Hospital')

# plotar cada rota com label
colors = plt.cm.tab10.colors
for i, (bairro, route) in enumerate(routes.items()):
    xs = [g.nodes[n]['x'] for n in route]
    ys = [g.nodes[n]['y'] for n in route]
    ax.plot(xs, ys,
            color=colors[i % len(colors)],
            linewidth=3,
            label=bairro)

ax.legend(title='Pontos e Rotas', loc='lower left', fontsize='small')
ax.set_title('Rotas Dijkstra (simples) - Hospital Walfredo Gurgel para bairros de Natal (Djikstra)')
plt.tight_layout()

# 14) Salvar e exibir
nome_arquivo = 'Rotas_Dijkstra_Simple.png'
fig.savefig(nome_arquivo, dpi=300, bbox_inches='tight')
plt.show()
