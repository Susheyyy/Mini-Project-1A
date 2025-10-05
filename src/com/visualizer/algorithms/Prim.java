package com.visualizer.algorithms;

import com.visualizer.models.Edge;
import com.visualizer.models.Graph;
import com.visualizer.models.Node;
import java.util.*;

public class Prim {
    public static List<AlgorithmStep> run(Graph graph, Node startNode) {
        List<AlgorithmStep> steps = new ArrayList<>();
        Map<Node, String> nodeColors = new HashMap<>();
        Map<Edge, String> edgeColors = new HashMap<>();
        graph.getNodes().forEach(node -> nodeColors.put(node, "unvisited"));

        Set<Node> mstNodes = new HashSet<>();
        PriorityQueue<Edge> pq = new PriorityQueue<>();

        mstNodes.add(startNode);
        nodeColors.put(startNode, "visited");
        graph.getAdjacentEdges(startNode).forEach(pq::add);
        steps.add(new AlgorithmStep(nodeColors, edgeColors, null, "Start with node " + startNode.getId() + ". Add its edges to the priority queue."));

        double totalWeight = 0;
        while (!pq.isEmpty() && mstNodes.size() < graph.getNodes().size()) {
            Edge minEdge = pq.poll();
            Node neighbor = mstNodes.contains(minEdge.getStart()) ? minEdge.getEnd() : minEdge.getStart();

            if (mstNodes.contains(neighbor)) {
                steps.add(new AlgorithmStep(nodeColors, edgeColors, null, "Edge (" + minEdge.getStart().getId() + "," + minEdge.getEnd().getId() + ") leads to an already visited node. Skip."));
                continue;
            }

            mstNodes.add(neighbor);
            nodeColors.put(neighbor, "visited");
            edgeColors.put(minEdge, "mst");
            totalWeight += minEdge.getWeight();
            steps.add(new AlgorithmStep(nodeColors, edgeColors, null, "Add edge (" + minEdge.getStart().getId() + "," + minEdge.getEnd().getId() + ") to MST. Total weight: " + String.format("%.0f", totalWeight)));


            for (Edge edge : graph.getAdjacentEdges(neighbor)) {
                if (!mstNodes.contains(edge.getEnd())) {
                    pq.add(edge);
                }
            }
        }
        steps.add(new AlgorithmStep(nodeColors, edgeColors, null, "Prim's algorithm finished. Final MST weight: " + String.format("%.0f", totalWeight)));
        return steps;
    }
}
