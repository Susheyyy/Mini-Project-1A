import time
from flask import Flask, request, jsonify, render_template
import heapq

# --- Basic Flask Setup ---
# The static_folder is set to 'static' to serve CSS and JS files.
# The template_folder is set to 'templates' for the HTML files.
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

# --- Utility Functions for Visualization State ---
def create_initial_state(nodes, edges):
    """Creates the initial visual state of the graph before an algorithm runs."""
    node_states = {str(i): {"color": "#60a5fa", "text": ""} for i in range(len(nodes))}
    edge_states = {f"{min(u,v)}-{max(u,v)}": {"color": "#94a3b8", "width": 3} for u, v, w in edges}
    return {"nodes": node_states, "edges": edge_states, "message": "Graph initialized."}

def deep_copy_state(state):
    """Creates a deep copy of a visualization state to avoid modifying previous steps."""
    return {
        "nodes": {k: v.copy() for k, v in state["nodes"].items()},
        "edges": {k: v.copy() for k, v in state["edges"].items()},
        "message": state["message"]
    }

# --- Algorithm Implementations (Provided by User) ---
# Each function now returns a tuple: (steps, final_message)

def dijkstra(graph_data):
    """Performs Dijkstra's algorithm and returns visualization steps."""
    nodes, edges, start_node = graph_data['nodes'], graph_data['edges'], graph_data['startNode']
    num_nodes = len(nodes)
    adj = {i: [] for i in range(num_nodes)}
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))

    distances = {i: float('inf') for i in range(num_nodes)}
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
                heapq.heappush(pq, (distances[v], v))
                
                current_state = deep_copy_state(steps[-1])
                current_state["nodes"][str(v)]["text"] = str(distances[v])
                current_state["nodes"][str(v)]["color"] = "#f59e0b"
                current_state["message"] = f"Updated dist of {nodes[v]} to {distances[v]}."
                steps.append(deep_copy_state(current_state))

            current_state = deep_copy_state(steps[-1])
            current_state["edges"][edge_key]["color"] = "#94a3b8"
            steps.append(deep_copy_state(current_state))
    
    final_message = "Dijkstra's finished."
    final_state = deep_copy_state(steps[-1])
    final_state["message"] = final_message
    steps.append(final_state)
    return steps, final_message

def bellman_ford(graph_data):
    """Performs Bellman-Ford algorithm and returns visualization steps."""
    nodes, edges, start_node = graph_data['nodes'], graph_data['edges'], graph_data['startNode']
    num_nodes = len(graph_data['nodes'])
    distances = {i: float('inf') for i in range(num_nodes)}
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
            for direction in [(u, v), (v, u)]: # Check both directions for undirected graph
                src, dest = direction
                if distances[src] != float('inf') and distances[src] + w < distances[dest]:
                    distances[dest] = distances[src] + w
                    current_state = deep_copy_state(steps[-1])
                    current_state["edges"][edge_key]["color"] = "#facc15"
                    current_state["nodes"][str(dest)]["text"] = str(distances[dest])
                    current_state["message"] = f"Relaxed edge {nodes[src]}-{nodes[dest]}. New dist for {nodes[dest]}: {distances[dest]}."
                    steps.append(deep_copy_state(current_state))
                    current_state["edges"][edge_key]["color"] = "#94a3b8"


    has_negative_cycle = any(distances[u] != float('inf') and distances[u] + w < distances[v] for u, v, w in edges)
    final_message = "Negative cycle detected!" if has_negative_cycle else "Bellman-Ford finished."
    final_state = deep_copy_state(steps[-1])
    final_state["message"] = final_message
    steps.append(final_state)
    return steps, final_message

def kruskal(graph_data):
    """Performs Kruskal's algorithm for MST and returns visualization steps."""
    nodes, edges, num_nodes = graph_data['nodes'], graph_data['edges'], len(graph_data['nodes'])
    sorted_edges, dsu, mst_cost = sorted(edges, key=lambda item: item[2]), DSU(num_nodes), 0
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
            current_state = deep_copy_state(steps[-1])
            current_state["edges"][edge_key]["color"] = "#10b981"
            current_state["edges"][edge_key]["width"] = 5
            current_state["nodes"][str(u)]["color"] = "#6ee7b7"
            current_state["nodes"][str(v)]["color"] = "#6ee7b7"
            current_state["message"] = f"Edge {nodes[u]}-{nodes[v]} added. MST cost: {mst_cost}."
            steps.append(deep_copy_state(current_state))
        else:
            current_state = deep_copy_state(steps[-1])
            current_state["edges"][edge_key]["color"] = "#ef4444"
            current_state["message"] = f"Edge {nodes[u]}-{nodes[v]} rejected (forms a cycle)."
            steps.append(deep_copy_state(current_state))
    
    final_message = f"Kruskal's finished. Final MST cost: {mst_cost}."
    final_state = deep_copy_state(steps[-1])
    final_state["message"] = final_message
    steps.append(final_state)
    return steps, final_message

def prim(graph_data):
    """Performs Prim's algorithm for MST and returns visualization steps."""
    nodes, edges, num_nodes = graph_data['nodes'], graph_data['edges'], len(graph_data['nodes'])
    start_node = 0 # Prim's can start anywhere
    adj = {i: [] for i in range(num_nodes)}
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    
    visited, min_heap, mst_cost = {i: False for i in range(num_nodes)}, [(0, start_node, -1)], 0
    steps = []
    
    current_state = create_initial_state(nodes, edges)
    current_state["message"] = f"Starting Prim's from node {nodes[start_node]}."
    steps.append(deep_copy_state(current_state))
    
    while min_heap and len([v for v in visited.values() if v]) < num_nodes:
        w, u, prev = heapq.heappop(min_heap)
        if visited[u]: continue
        
        visited[u] = True
        mst_cost += w
        
        current_state = deep_copy_state(steps[-1])
        current_state["nodes"][str(u)]["color"] = "#6ee7b7"
        
        if prev != -1:
            edge_key = f"{min(prev, u)}-{max(prev, u)}"
            current_state["edges"][edge_key]["color"] = "#10b981"
            current_state["edges"][edge_key]["width"] = 5
        current_state["message"] = f"Added node {nodes[u]}. Current MST cost: {mst_cost}."
        steps.append(deep_copy_state(current_state))
        
        for v, weight in adj[u]:
            if not visited[v]:
                heapq.heappush(min_heap, (weight, v, u))
    
    final_message = f"Prim's finished. Final MST cost: {mst_cost}."
    final_state = deep_copy_state(steps[-1])
    final_state["message"] = final_message
    steps.append(final_state)
    return steps, final_message

# --- Algorithm Runner Helper ---
def run_single_algorithm(algo_name, graph_data):
    """Runs a single algorithm, measures its execution time, and returns results."""
    algorithms = {
        'dijkstra': dijkstra,
        'bellman-ford': bellman_ford,
        'kruskal': kruskal,
        'prim': prim
    }
    if algo_name not in algorithms:
        return {"error": f"Algorithm '{algo_name}' not found."}

    start_time = time.perf_counter()
    steps, final_message = algorithms[algo_name](graph_data)
    end_time = time.perf_counter()
    
    execution_time_ms = (end_time - start_time) * 1000
    
    return {
        "steps": steps,
        "execution_time": round(execution_time_ms, 2),
        "final_message": final_message
    }


# --- Flask Routes ---
@app.route('/')
def index():
    """Serves the main landing page."""
    return render_template('index.html')

@app.route('/visualizer')
def visualizer_page():
    """Serves the algorithm visualizer page."""
    return render_template('visualizer.html')

@app.route('/compare')
def compare_page():
    """Serves the algorithm comparison page."""
    return render_template('compare.html')


# --- API Endpoints ---
@app.route('/api/run_algorithm', methods=['POST'])
def api_run_algorithm():
    """API endpoint for the single visualizer page."""
    try:
        data = request.json
        graph_data = data['graph']
        graph_data['nodes'] = [chr(65 + i) for i in graph_data['nodes']] # Map IDs to letters
        
        result = run_single_algorithm(data['algorithm'], graph_data)
        if "error" in result:
            return jsonify({"error": result["error"]}), 400
        return jsonify(result["steps"])
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/compare_algorithms', methods=['POST'])
def api_compare_algorithms():
    """API endpoint for the comparison page."""
    try:
        data = request.json
        graph_data = data['graph']
        algo1_name = data['algo1']
        algo2_name = data['algo2']

        # Map node IDs to letters for display purposes in the algorithms
        graph_data['nodes'] = [chr(65 + i) for i in graph_data['nodes']]
        
        # Run both algorithms
        result1 = run_single_algorithm(algo1_name, graph_data.copy())
        result2 = run_single_algorithm(algo2_name, graph_data.copy())

        if "error" in result1 or "error" in result2:
            return jsonify({"error": result1.get("error") or result2.get("error")}), 400

        return jsonify({
            "algo1_result": result1,
            "algo2_result": result2,
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)

