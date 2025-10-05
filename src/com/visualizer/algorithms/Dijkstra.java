package com.visualizer.algorithms;

import com.visualizer.models.Edge;
import com.visualizer.models.Graph;
import com.visualizer.models.Node;
import java.util.*;

public class Dijkstra {
    public static List<AlgorithmStep> run(Graph graph, Node startNode) {
        List<AlgorithmStep> steps = new ArrayList<>();
        Map<Node, String> nodeColors = new HashMap<>();
        Map<Edge, String> edgeColors = new HashMap<>();
        graph.getNodes().forEach(node -> nodeColors.put(node, "unvisited"));

        Map<Node, Double> distances = new HashMap<>();
        Map<Node, Node> predecessors = new HashMap<>();
        PriorityQueue<Node> pq = new PriorityQueue<>(Comparator.comparingDouble(distances::get));

        for (Node node : graph.getNodes()) {
            distances.put(node, Double.MAX_VALUE);
            predecessors.put(node, null);
        }
        distances.put(startNode, 0.0);
        pq.add(startNode);
        steps.add(new AlgorithmStep(nodeColors, edgeColors, distances, "Initialization: Distances set to infinity, 0 for start node."));

        while (!pq.isEmpty()) {
            Node currentNode = pq.poll();
            nodeColors.put(currentNode, "visited");
            steps.add(new AlgorithmStep(nodeColors, edgeColors, distances, "Visiting node " + currentNode.getId() + "."));

            for (Edge edge : graph.getAdjacentEdges(currentNode)) {
                Node neighbor = edge.getEnd();
                if (nodeColors.get(neighbor).equals("visited")) continue;

                double newDist = distances.get(currentNode) + edge.getWeight();
                if (newDist < distances.get(neighbor)) {
                    distances.put(neighbor, newDist);
                    predecessors.put(neighbor, currentNode);
                    pq.remove(neighbor);
                    pq.add(neighbor);
                    steps.add(new AlgorithmStep(nodeColors, edgeColors, distances, "Relaxing edge (" + currentNode.getId() + ", " + neighbor.getId() + "). New distance for " + neighbor.getId() + " is " + String.format("%.0f", newDist) + "."));
                }
            }

        }
        steps.add(new AlgorithmStep(nodeColors, edgeColors, distances, "Dijkstra's algorithm finished."));
        return steps;
    }
}
