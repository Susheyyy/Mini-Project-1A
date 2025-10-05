package com.visualizer.algorithms;

import com.visualizer.models.Edge;
import com.visualizer.models.Node;
import java.util.Map;
import java.util.HashMap;

public class AlgorithmStep {
    public final Map<Node, String> nodeColors;
    public final Map<Edge, String> edgeColors;
    public final Map<Node, Double> nodeDistances;
    public final String logMessage;

    public AlgorithmStep(Map<Node, String> nodeColors, Map<Edge, String> edgeColors, Map<Node, Double> nodeDistances, String logMessage) {
        this.nodeColors = (nodeColors != null) ? new HashMap<>(nodeColors) : new HashMap<>();
        this.edgeColors = (edgeColors != null) ? new HashMap<>(edgeColors) : new HashMap<>();
        this.nodeDistances = (nodeDistances != null) ? new HashMap<>(nodeDistances) : null;
        this.logMessage = logMessage;
    }
}
