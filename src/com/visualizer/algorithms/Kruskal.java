package com.visualizer.algorithms;

import com.visualizer.models.Edge;
import com.visualizer.models.Graph;
import com.visualizer.models.Node;
import java.util.*;

public class Kruskal {

    // Helper class for Disjoint Set Union (DSU)
    private static class DSU {
        private final Map<Node, Node> parent = new HashMap<>();
        public void makeSet(Node node) { parent.put(node, node); }
        public Node find(Node node) {
            if (parent.get(node) == node) return node;
            return find(parent.get(node));
        }
        public void union(Node node1, Node node2) {
            Node root1 = find(node1);
            Node root2 = find(node2);
            if (root1 != root2) parent.put(root1, root2);
        }
    }

    public static List<AlgorithmStep> run(Graph graph) {
        List<AlgorithmStep> steps = new ArrayList<>();
        Map<Node, String> nodeColors = new HashMap<>();
        Map<Edge, String> edgeColors = new HashMap<>();
        graph.getNodes().forEach(node -> nodeColors.put(node, "unvisited"));

        List<Edge> sortedEdges = new ArrayList<>(graph.getEdges());
        Collections.sort(sortedEdges);
        steps.add(new AlgorithmStep(nodeColors, edgeColors, null, "Sort all edges by weight."));

        DSU dsu = new DSU();
        graph.getNodes().forEach(dsu::makeSet);

        double totalWeight = 0;
        for (Edge edge : sortedEdges) {
            edgeColors.put(edge, "processing");
            steps.add(new AlgorithmStep(nodeColors, edgeColors, null, "Considering edge (" + edge.getStart().getId() + "," + edge.getEnd().getId() + ") with weight " + edge.getWeight() + "."));

            if (dsu.find(edge.getStart()) != dsu.find(edge.getEnd())) {
                dsu.union(edge.getStart(), edge.getEnd());
                edgeColors.put(edge, "mst");
                totalWeight += edge.getWeight();
                steps.add(new AlgorithmStep(nodeColors, edgeColors, null, "Edge does not form a cycle. Add to MST. Total weight: " + String.format("%.0f", totalWeight)));
            } else {
                edgeColors.put(edge, "discarded");
                steps.add(new AlgorithmStep(nodeColors, edgeColors, null, "Edge forms a cycle. Discard."));
            }
        }
        steps.add(new AlgorithmStep(nodeColors, edgeColors, null, "Kruskal's algorithm finished. Final MST weight: " + String.format("%.0f", totalWeight)));
        return steps;
    }
}
