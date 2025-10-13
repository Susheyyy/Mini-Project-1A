import time
from flask import Flask, request, jsonify, render_template
import heapq

# --- Basic Flask Setup ---
app = Flask(__name__,
            static_folder='static',
            template_folder='templates',
            static_url_path='/static')

# --- Disjoint Set Union (DSU) for Kruskal's Algorithm ---
class DSU:
    """A helper class for the Disjoint Set Union data structure."""
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, i):
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            self.parent[root_i] = root_j
            return True
        return False

# --- Utility Functions ---
def create_initial_state(nodes, edges):
    """Creates the initial visual state of the graph."""
    node_states = {str(i): {"color": "#60a5fa", "text": ""} for i in range(len(nodes))}
    edge_states = {f"{min(u,v)}-{max(u,v)}": {"color": "#94a3b8", "width": 3} for u, v, w in edges}
    return {"nodes": node_states, "edges": edge_states, "message": "Graph initialized."}

def deep_copy_state(state):
    """Creates a deep copy of a visualization state."""
    return {
        "nodes": {k: v.copy() for k, v in state["nodes"].items()},
        "edges": {k: v.copy() for k, v in state["edges"].items()},
        "message": state["message"]
    }

def get_path_string(start_node, end_node, predecessors, nodes_map):
    """Constructs a string representation of the path."""
    path = []
    curr = end_node
    while curr is not None:
        path.append(nodes_map[curr])
        curr = predecessors[curr]
    if not path or path[-1] != nodes_map[start_node]: return "Not reachable"
    return " -> ".join(reversed(path))

# --- Algorithm Implementations ---

def dijkstra(graph_data):
    nodes, edges, start_node = graph_data['nodes'], graph_data['edges'], graph_data['startNode']
    num_nodes = len(nodes)
    adj = {i: [] for i in range(num_nodes)}
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))

    distances = {i: float('inf') for i in range(num_nodes)}
    predecessor = {i: None for i in range(num_nodes)}
    distances[start_node] = 0
    pq = [(0, start_node)]
    steps = []

    current_state = create_initial_state(nodes, edges)
    current_state["message"] = f"Starting Dijkstra's from node {nodes[start_node]}."
    for i in range(num_nodes):
         current_state["nodes"][str(i)]["text"] = "∞"
    current_state["nodes"][str(start_node)]["text"] = "0"
    current_state["nodes"][str(start_node)]["color"] = "#f59e0b"
    steps.append(deep_copy_state(current_state))

    while pq:
        dist, u = heapq.heappop(pq)
        if dist > distances[u]: continue

        current_state = deep_copy_state(steps[-1])
        current_state["nodes"][str(u)]["color"] = "#4f46e5"
        current_state["message"] = f"Visiting node {nodes[u]}. Dist: {dist}."
        steps.append(deep_copy_state(current_state))

        for v, weight in adj[u]:
            edge_key = f"{min(u,v)}-{max(u,v)}"
            current_state = deep_copy_state(steps[-1])
            current_state["edges"][edge_key]["color"] = "#facc15"
            current_state["message"] = f"Checking edge {nodes[u]}-{nodes[v]}."
            steps.append(deep_copy_state(current_state))

            if distances[u] + weight < distances[v]:
                distances[v] = distances[u] + weight
                predecessor[v] = u
                heapq.heappush(pq, (distances[v], v))
                
                current_state = deep_copy_state(steps[-1])
                current_state["nodes"][str(v)]["text"] = str(distances[v])
                current_state["nodes"][str(v)]["color"] = "#f59e0b"
                current_state["message"] = f"Updated dist of {nodes[v]} to {distances[v]}."
                steps.append(deep_copy_state(current_state))

            current_state = deep_copy_state(steps[-1])
            current_state["edges"][edge_key]["color"] = "#94a3b8"
            steps.append(deep_copy_state(current_state))
    
    final_state = deep_copy_state(steps[-1])
    path_messages = ["Explanation: Shortest Paths:"]
    for i in range(num_nodes):
        if i != start_node:
            path_str = get_path_string(start_node, i, predecessor, nodes)
            dist = distances[i] if distances[i] != float('inf') else 'infinity'
            path_messages.append(f"For {nodes[start_node]} to {nodes[i]} minimum distance is {dist}. Path: {path_str}")

    final_state["message"] = "<br>".join(path_messages)
    steps.append(final_state)
    return steps, final_state["message"]


def bellman_ford(graph_data):
    nodes, edges, start_node = graph_data['nodes'], graph_data['edges'], graph_data['startNode']
    num_nodes = len(nodes)
    distances = {i: float('inf') for i in range(num_nodes)}
    predecessor = {i: None for i in range(num_nodes)}
    distances[start_node] = 0
    steps = []

    current_state = create_initial_state(nodes, edges)
    current_state["message"] = f"Starting Bellman-Ford from {nodes[start_node]}."
    for i in range(num_nodes):
        current_state["nodes"][str(i)]["text"] = "∞"
    current_state["nodes"][str(start_node)]["text"] = "0"
    steps.append(deep_copy_state(current_state))
    
    for i in range(num_nodes - 1):
        current_state = deep_copy_state(steps[-1])
        current_state["message"] = f"Iteration {i + 1}: Relaxing edges."
        steps.append(deep_copy_state(current_state))
        
        for u, v, w in edges:
            edge_key = f"{min(u,v)}-{max(u,v)}"
            for direction in [(u, v, w), (v, u, w)]:
                src, dest, weight = direction
                if distances[src] != float('inf') and distances[src] + weight < distances[dest]:
                    distances[dest] = distances[src] + weight
                    predecessor[dest] = src
                    current_state = deep_copy_state(steps[-1])
                    current_state["edges"][edge_key]["color"] = "#facc15"
                    current_state["nodes"][str(dest)]["text"] = str(distances[dest])
                    current_state["message"] = f"Relaxed edge {nodes[src]}-{nodes[dest]}. New dist for {nodes[dest]}: {distances[dest]}."
                    steps.append(deep_copy_state(current_state))
                    current_state["edges"][edge_key]["color"] = "#94a3b8"

    final_state = deep_copy_state(steps[-1])
    for u, v, w in edges:
        if distances[u] != float('inf') and distances[u] + w < distances[v]:
            final_state["message"] = "Explanation: The graph contains a negative weight cycle."
            steps.append(final_state)
            return steps, final_state["message"]

    path_messages = ["Explanation: Shortest Paths:"]
    for i in range(num_nodes):
        if i != start_node:
            path_str = get_path_string(start_node, i, predecessor, nodes)
            dist = distances[i] if distances[i] != float('inf') else 'infinity'
            path_messages.append(f"For {nodes[start_node]} to {nodes[i]} minimum distance is {dist}. Path: {path_str}")
        
    final_state["message"] = "<br>".join(path_messages)
    steps.append(final_state)
    return steps, final_state["message"]


def kruskal(graph_data):
    nodes, edges, num_nodes = graph_data['nodes'], graph_data['edges'], len(graph_data['nodes'])
    sorted_edges, dsu, mst_cost, mst_edges = sorted(edges, key=lambda item: item[2]), DSU(num_nodes), 0, []
    steps = []
    
    current_state = create_initial_state(nodes, edges)
    current_state["message"] = "Starting Kruskal's. Edges sorted by weight."
    steps.append(deep_copy_state(current_state))
    
    for u, v, w in sorted_edges:
        edge_key = f"{min(u,v)}-{max(u,v)}"
        current_state = deep_copy_state(steps[-1])
        current_state["edges"][edge_key]["color"] = "#facc15"
        current_state["message"] = f"Considering edge {nodes[u]}-{nodes[v]} (Weight: {w})."
        steps.append(deep_copy_state(current_state))
        
        if dsu.union(u, v):
            mst_cost += w
            mst_edges.append((nodes[u], nodes[v], w))
            current_state = deep_copy_state(steps[-1])
            current_state["edges"][edge_key]["color"] = "#10b981"
            current_state["edges"][edge_key]["width"] = 5
            current_state["message"] = f"Edge {nodes[u]}-{nodes[v]} added. MST cost: {mst_cost}."
            steps.append(deep_copy_state(current_state))
        else:
            current_state = deep_copy_state(steps[-1])
            current_state["edges"][edge_key]["color"] = "#ef4444"
            current_state["message"] = f"Edge {nodes[u]}-{nodes[v]} rejected (forms a cycle)."
            steps.append(deep_copy_state(current_state))
    
    final_state = deep_copy_state(steps[-1])
    edge_strings = [f"{u}-{v} (Weight: {w})" for u, v, w in mst_edges]
    final_state["message"] = (f"Explanation: Kruskal's algorithm found the MST with a total cost of {mst_cost}. "
                              f"Edges in MST: {', '.join(edge_strings)}.")
    steps.append(final_state)
    return steps, final_state["message"]


def prim(graph_data):
    nodes, edges, num_nodes = graph_data['nodes'], graph_data['edges'], len(graph_data['nodes'])
    start_node = 0
    adj = {i: [] for i in range(num_nodes)}
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    
    visited, min_heap, mst_cost, mst_edges = set(), [(0, start_node, -1)], 0, []
    steps = []
    
    current_state = create_initial_state(nodes, edges)
    current_state["message"] = f"Starting Prim's from node {nodes[start_node]}."
    steps.append(deep_copy_state(current_state))
    
    while min_heap and len(visited) < num_nodes:
        w, u, prev = heapq.heappop(min_heap)
        if u in visited: continue
        
        visited.add(u)
        mst_cost += w
        
        current_state = deep_copy_state(steps[-1])
        current_state["nodes"][str(u)]["color"] = "#6ee7b7"
        
        if prev != -1:
            mst_edges.append((nodes[prev], nodes[u], w))
            edge_key = f"{min(prev, u)}-{max(prev, u)}"
            current_state["edges"][edge_key]["color"] = "#10b981"
            current_state["edges"][edge_key]["width"] = 5
        current_state["message"] = f"Added node {nodes[u]}. Current MST cost: {mst_cost}."
        steps.append(deep_copy_state(current_state))
        
        for v, weight in adj[u]:
            if v not in visited:
                heapq.heappush(min_heap, (weight, v, u))
    
    final_state = deep_copy_state(steps[-1])
    edge_strings = [f"{u}-{v} (Weight: {w})" for u, v, w in mst_edges]
    final_state["message"] = (f"Explanation: Prim's algorithm found the MST with a total cost of {mst_cost}. "
                              f"Edges in MST: {', '.join(edge_strings)}.")
    steps.append(final_state)
    return steps, final_state["message"]

# --- Algorithm Runner ---
def run_single_algorithm(algo_name, graph_data):
    algorithms = {
        'dijkstra': dijkstra, 'bellman-ford': bellman_ford,
        'kruskal': kruskal, 'prim': prim
    }
    if algo_name not in algorithms:
        return {"error": f"Algorithm '{algo_name}' not found."}
    
    if algo_name != 'bellman-ford':
        if any(w < 0 for _, _, w in graph_data['edges']):
            return {"error": f"{algo_name.capitalize()}'s algorithm does not support negative weights."}

    start_time = time.perf_counter()
    steps, final_message = algorithms[algo_name](graph_data)
    end_time = time.perf_counter()
    
    return {
        "steps": steps,
        "execution_time": round((end_time - start_time) * 1000, 2),
        "final_message": final_message
    }

# --- Flask Routes and API Endpoints (No changes needed below this line) ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/visualizer')
def visualizer_page(): return render_template('visualizer.html')

@app.route('/compare')
def compare_page(): return render_template('compare.html')

@app.route('/api/run_algorithm', methods=['POST'])
def api_run_algorithm():
    try:
        data = request.json
        graph_data = data['graph']
        graph_data['nodes'] = [chr(65 + i) for i in graph_data['nodes']]
        
        result = run_single_algorithm(data['algorithm'], graph_data)
        if "error" in result: return jsonify({"error": result["error"]}), 400
        return jsonify(result["steps"])
        
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/api/compare_algorithms', methods=['POST'])
def api_compare_algorithms():
    try:
        data = request.json
        graph_data = data['graph']
        graph_data['nodes'] = [chr(65 + i) for i in graph_data['nodes']]
        
        result1 = run_single_algorithm(data['algo1'], graph_data.copy())
        result2 = run_single_algorithm(data['algo2'], graph_data.copy())

        if "error" in result1 or "error" in result2:
            return jsonify({"error": result1.get("error") or result2.get("error")}), 400

        return jsonify({"algo1_result": result1, "algo2_result": result2})
    except Exception as e: return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)