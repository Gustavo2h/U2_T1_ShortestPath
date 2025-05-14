import time
import osmnx as ox
import pandas as pd
from codecarbon import EmissionsTracker
import matplotlib.pyplot as plt

# Configurações
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

# Geocodificar
hospital_point = ox.geocode(hospital_address)
bairro_points = {bairro: ox.geocode(addr) for bairro, addr in bairro_addresses.items()}

# Obter grafo de direção
print("Carregando grafo de Natal...")
g = ox.graph_from_place("Natal, Rio Grande do Norte, Brazil", network_type="drive")
g = ox.add_edge_speeds(g)
g = ox.add_edge_travel_times(g)

# Nós de origem e destino
orig_node = ox.nearest_nodes(g, hospital_point[1], hospital_point[0])
dest_nodes = {bairro: ox.nearest_nodes(g, pt[1], pt[0]) for bairro, pt in bairro_points.items()}

# Iniciar Coleta de Emissões e Temporização
tracker = EmissionsTracker()
tracker.start()
start = time.time()

# Avaliar rotas usando funções do OSMnx
dados = []
routes = {}
for bairro, dest_node in dest_nodes.items():
    route = ox.shortest_path(g, orig_node, dest_node, weight='travel_time')
    routes[bairro] = route

    # Extrair atributos do trajeto
    dist_m = 0
    time_s = 0
    for u, v in zip(route[:-1], route[1:]):
        edge_data = g.get_edge_data(u, v)
        key = next(iter(edge_data))
        attrs = edge_data[key]
        dist_m += attrs.get('length', 0)
        time_s += attrs.get('travel_time', 0)

    # Converter para km e minutos
    dados.append({
        'Bairro': bairro,
        'Distância (km)': round(dist_m / 1000, 2),
        'Tempo de Resposta (min)': round(time_s / 60, 1)
    })

# Finaliza métricas
elapsed = time.time() - start
emiss = tracker.stop()

# Exibir tabela de resultados
df = pd.DataFrame(dados).sort_values('Bairro').reset_index(drop=True)
print(df.to_string(index=False))
print(f"\nTempo de execução: {elapsed:.2f} s")
print(f"Emissão de carbono: {emiss:.6f} kg CO₂")

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
hx = g.nodes[orig_node]['x']
hy = g.nodes[orig_node]['y']
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
ax.set_title('Rotas do Hospital Walfredo Gurgel para bairros de Natal (OSMnx)')
plt.tight_layout()

# Salvar figura
nome_arquivo = 'Rotas_OSM.png'
fig.savefig(nome_arquivo, dpi=300, bbox_inches='tight')
plt.show()
