# app.py - FIXED VERSION
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import heapq
import json

# --- Basic Setup ---
app = Flask(__name__, static_folder='.', template_folder='.', static_url_path='')
CORS(app)

# --- Disjoint Set Union (DSU) for Kruskal's Algorithm ---
class DSU:
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

# --- Utility Function to create a base state snapshot ---
def create_initial_state(nodes, edges):
    """Creates the initial visual state of the graph."""
    node_states = {str(i): {"color": "#60a5fa", "text": ""} for i in range(len(nodes))}
    edge_states = {f"{min(u,v)}-{max(u,v)}": {"color": "#94a3b8", "width": 3} for u, v, w in edges}
    return {"nodes": node_states, "edges": edge_states, "message": "Graph initialized."}

def deep_copy_state(state):
    """Create a deep copy of the state."""
    return {
        "nodes": {k: v.copy() for k, v in state["nodes"].items()},
        "edges": {k: v.copy() for k, v in state["edges"].items()},
        "message": state["message"]
    }

# --- Algorithm Implementations ---

def dijkstra(graph_data):
    nodes = graph_data['nodes']
    edges = graph_data['edges']
    start_node = graph_data['startNode']
    num_nodes = len(nodes)
    
    adj = {i: [] for i in range(num_nodes)}
    # Build an UNDIRECTED graph for Dijkstra
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))

    distances = {i: float('inf') for i in range(num_nodes)}
    distances[start_node] = 0
    pq = [(0, start_node)]

    steps = []
    current_state = create_initial_state(nodes, edges)
    current_state["message"] = f"Starting Dijkstra's Algorithm from node {nodes[start_node]}."
    for i in range(num_nodes):
         current_state["nodes"][str(i)]["text"] = "∞"
    current_state["nodes"][str(start_node)]["text"] = "0"
    current_state["nodes"][str(start_node)]["color"] = "#f59e0b"
    steps.append(deep_copy_state(current_state))

    while pq:
        dist, u = heapq.heappop(pq)

        if dist > distances[u]:
            continue
        
        current_state = deep_copy_state(steps[-1])
        current_state["nodes"][str(u)]["color"] = "#4f46e5"
        current_state["message"] = f"Visiting node {nodes[u]}. Current distance: {dist}."
        steps.append(deep_copy_state(current_state))

        for v, weight in adj[u]:
            current_state = deep_copy_state(steps[-1])
            edge_key = f"{min(u,v)}-{max(u,v)}"
            current_state["edges"][edge_key]["color"] = "#facc15"
            current_state["message"] = f"Considering edge from {nodes[u]} to {nodes[v]} with weight {weight}."
            steps.append(deep_copy_state(current_state))
            
            if distances[u] + weight < distances[v]:
                distances[v] = distances[u] + weight
                heapq.heappush(pq, (distances[v], v))
                
                current_state = deep_copy_state(steps[-1])
                current_state["nodes"][str(v)]["text"] = str(distances[v])
                current_state["nodes"][str(v)]["color"] = "#f59e0b"
                current_state["message"] = f"Updated distance of node {nodes[v]} to {distances[v]}."
                steps.append(deep_copy_state(current_state))

            current_state = deep_copy_state(steps[-1])
            current_state["edges"][edge_key]["color"] = "#94a3b8"
            steps.append(deep_copy_state(current_state))

    final_state = deep_copy_state(steps[-1])
    final_state["message"] = "Dijkstra's Algorithm finished."
    steps.append(final_state)
    return steps

def bellman_ford(graph_data):
    nodes, edges, start_node, num_nodes = graph_data['nodes'], graph_data['edges'], graph_data['startNode'], len(graph_data['nodes'])
    distances = {i: float('inf') for i in range(num_nodes)}
    distances[start_node] = 0
    
    steps = []
    current_state = create_initial_state(nodes, edges)
    current_state["message"] = f"Starting Bellman-Ford from node {nodes[start_node]}."
    for i in range(num_nodes):
        current_state["nodes"][str(i)]["text"] = "∞"
    current_state["nodes"][str(start_node)]["text"] = "0"
    steps.append(deep_copy_state(current_state))
    
    for i in range(num_nodes - 1):
        current_state = deep_copy_state(steps[-1])
        current_state["message"] = f"Iteration {i + 1}: Relaxing all edges."
        steps.append(deep_copy_state(current_state))
        
        for u, v, w in edges:
            edge_key = f"{min(u,v)}-{max(u,v)}"
            current_state = deep_copy_state(steps[-1])
            current_state["edges"][edge_key]["color"] = "#facc15"
            steps.append(deep_copy_state(current_state))
            
            if distances[u] != float('inf') and distances[u] + w < distances[v]:
                distances[v] = distances[u] + w
                current_state = deep_copy_state(steps[-1])
                current_state["nodes"][str(v)]["text"] = str(distances[v])
                current_state["message"] = f"Relaxed edge {nodes[u]}-{nodes[v]}. New distance for {nodes[v]} is {distances[v]}."
                steps.append(deep_copy_state(current_state))
            
            current_state = deep_copy_state(steps[-1])
            current_state["edges"][edge_key]["color"] = "#94a3b8"
            steps.append(deep_copy_state(current_state))
    
    has_negative_cycle = any(distances[u] != float('inf') and distances[u] + w < distances[v] for u, v, w in edges)
    final_state = deep_copy_state(steps[-1])
    final_state["message"] = "Negative weight cycle detected!" if has_negative_cycle else "Bellman-Ford finished."
    steps.append(final_state)
    return steps

def kruskal(graph_data):
    nodes, edges, num_nodes = graph_data['nodes'], graph_data['edges'], len(graph_data['nodes'])
    sorted_edges, dsu, mst_cost = sorted(edges, key=lambda item: item[2]), DSU(num_nodes), 0
    
    steps = []
    current_state = create_initial_state(nodes, edges)
    current_state["message"] = "Starting Kruskal's Algorithm. Edges are sorted by weight."
    steps.append(deep_copy_state(current_state))
    
    for u, v, w in sorted_edges:
        edge_key = f"{min(u,v)}-{max(u,v)}"
        current_state = deep_copy_state(steps[-1])
        current_state["edges"][edge_key]["color"] = "#facc15"
        current_state["message"] = f"Considering edge {nodes[u]}-{nodes[v]} with weight {w}."
        steps.append(deep_copy_state(current_state))
        
        if dsu.union(u, v):
            mst_cost += w
            current_state = deep_copy_state(steps[-1])
            current_state["edges"][edge_key]["color"] = "#10b981"
            current_state["edges"][edge_key]["width"] = 5
            current_state["nodes"][str(u)]["color"] = "#6ee7b7"
            current_state["nodes"][str(v)]["color"] = "#6ee7b7"
            current_state["message"] = f"Edge {nodes[u]}-{nodes[v]} added to MST. Cost: {mst_cost}."
            steps.append(deep_copy_state(current_state))
        else:
            current_state = deep_copy_state(steps[-1])
            current_state["edges"][edge_key]["color"] = "#ef4444"
            current_state["message"] = f"Edge {nodes[u]}-{nodes[v]} rejected (forms a cycle)."
            steps.append(deep_copy_state(current_state))
    
    final_state = deep_copy_state(steps[-1])
    final_state["message"] = f"Kruskal's Algorithm finished. Final MST cost: {mst_cost}."
    steps.append(final_state)
    return steps

def prim(graph_data):
    nodes, edges, start_node, num_nodes = graph_data['nodes'], graph_data['edges'], 0, len(graph_data['nodes'])
    adj = {i: [] for i in range(num_nodes)}
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    
    visited, min_heap, mst_cost = {i: False for i in range(num_nodes)}, [(0, start_node, -1)], 0
    
    steps = []
    current_state = create_initial_state(nodes, edges)
    current_state["message"] = f"Starting Prim's Algorithm from node {nodes[start_node]}."
    steps.append(deep_copy_state(current_state))
    
    while min_heap and len([v for v in visited.values() if v]) < num_nodes:
        w, u, prev = heapq.heappop(min_heap)
        if visited[u]:
            continue
        visited[u] = True
        mst_cost = mst_cost + w
        
        current_state = deep_copy_state(steps[-1])
        current_state["nodes"][str(u)]["color"] = "#6ee7b7"
        
        if prev != -1:
            edge_key = f"{min(prev, u)}-{max(prev, u)}"
            current_state["edges"][edge_key]["color"] = "#10b981"
            current_state["edges"][edge_key]["width"] = 5
            current_state["message"] = f"Added node {nodes[u]} from {nodes[prev]}. Cost: {mst_cost}."
        else:
            current_state["message"] = f"Added starting node {nodes[u]} to MST."
        steps.append(deep_copy_state(current_state))
        
        for v, weight in adj[u]:
            if not visited[v]:
                heapq.heappush(min_heap, (weight, v, u))
    
    final_state = deep_copy_state(steps[-1])
    final_state["message"] = f"Prim's Algorithm finished. Final MST cost: {mst_cost}."
    steps.append(final_state)
    return steps

# --- API Endpoint & Main Route ---
@app.route('/api/run_algorithm', methods=['POST'])
def run_algorithm():
    """API endpoint to run a selected graph algorithm."""
    try:
        data = request.json
        print("Received data:", data)  # Debug logging
        
        graph_data = data['graph']
        
        # Convert node IDs to letters for display
        graph_data['nodes'] = [chr(65 + i) for i in graph_data['nodes']]
        
        algorithm = data.get('algorithm')
        algorithms = {
            'dijkstra': dijkstra, 
            'bellman-ford': bellman_ford, 
            'kruskal': kruskal, 
            'prim': prim
        }
        
        if algorithm in algorithms:
            steps = algorithms[algorithm](graph_data)
            print(f"Generated {len(steps)} steps")  # Debug logging
            return jsonify(steps)
        else:
            return jsonify({"error": "Algorithm not found"}), 400
            
    except Exception as e:
        print(f"Error: {str(e)}")  # Debug logging
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    """Serves the main index.html file."""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)