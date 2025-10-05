package com.visualizer.models;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Graph {
    private final List<Node> nodes;
    private final List<Edge> edges;
    private final Map<Node, List<Edge>> adjacencyList;

    public Graph() {
        this.nodes = new ArrayList<>();
        this.edges = new ArrayList<>();
        this.adjacencyList = new HashMap<>();
        Node.resetIdCounter();
    }

    public void addNode(Node node) {
        nodes.add(node);
        adjacencyList.put(node, new ArrayList<>());
    }

    public void addEdge(Node start, Node end) {
        for (Edge edge : adjacencyList.get(start)) {
            if (edge.getEnd().equals(end) || edge.getStart().equals(end)) {
                return;
            }
        }
        Edge newEdge = new Edge(start, end);
        edges.add(newEdge);
        adjacencyList.get(start).add(newEdge);
        adjacencyList.get(end).add(new Edge(end, start)); // For undirected graph logic
    }

    public List<Node> getNodes() { return nodes; }
    public List<Edge> getEdges() { return edges; }
    public List<Edge> getAdjacentEdges(Node node) { return adjacencyList.getOrDefault(node, new ArrayList<>()); }

    public void clear() {
        nodes.clear();
        edges.clear();
        adjacencyList.clear();
        Node.resetIdCounter();
    }
}
