package com.visualizer.algorithms;

import com.visualizer.models.Edge;
import com.visualizer.models.Graph;
import com.visualizer.models.Node;
import java.util.*;

public class BellmanFord {
    public static List<AlgorithmStep> run(Graph graph, Node startNode) {
        List<AlgorithmStep> steps = new ArrayList<>();
        Map<Node, String> nodeColors = new HashMap<>();
        Map<Edge, String> edgeColors = new HashMap<>();
        graph.getNodes().forEach(node -> nodeColors.put(node, "unvisited"));

        Map<Node, Double> distances = new HashMap<>();
        for (Node node : graph.getNodes()) {
            distances.put(node, Double.MAX_VALUE);
        }
        distances.put(startNode, 0.0);
        steps.add(new AlgorithmStep(nodeColors, edgeColors, distances, "Initialization complete."));

        for (int i = 0; i < graph.getNodes().size() - 1; i++) {
            boolean relaxed = false;
            for (Edge edge : graph.getEdges()) {
                if (distances.get(edge.getStart()) + edge.getWeight() < distances.get(edge.getEnd())) {
                    distances.put(edge.getEnd(), distances.get(edge.getStart()) + edge.getWeight());
                    relaxed = true;
                }
                // Also check the reverse for undirected graph representation
                 if (distances.get(edge.getEnd()) + edge.getWeight() < distances.get(edge.getStart())) {
                    distances.put(edge.getStart(), distances.get(edge.getEnd()) + edge.getWeight());
                    relaxed = true;
                }
            }
            steps.add(new AlgorithmStep(nodeColors, edgeColors, distances, "After relaxation pass " + (i + 1) + "."));
            if (!relaxed) break; // Optimization
        }

        // Check for negative weight cycles
        for (Edge edge : graph.getEdges()) {
            if (distances.get(edge.getStart()) + edge.getWeight() < distances.get(edge.getEnd())) {
                steps.add(new AlgorithmStep(nodeColors, edgeColors, distances, "Negative weight cycle detected!"));
                return steps;
            }
        }

        steps.add(new AlgorithmStep(nodeColors, edgeColors, distances, "Bellman-Ford finished."));
        return steps;
    }
}
