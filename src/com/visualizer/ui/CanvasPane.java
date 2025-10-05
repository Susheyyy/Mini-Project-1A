package com.visualizer.ui;

import com.visualizer.models.Edge;
import com.visualizer.models.Graph;
import com.visualizer.models.Node;
import javafx.scene.canvas.Canvas;
import javafx.scene.canvas.GraphicsContext;
import javafx.scene.layout.Pane;
import javafx.scene.paint.Color;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;
import javafx.scene.text.TextAlignment;
import java.util.Map;

public class CanvasPane extends Pane {
    private final Canvas canvas;
    private Graph graph;
    private Map<Node, String> nodeColors;
    private Map<Edge, String> edgeColors;
    private Map<Node, Double> nodeDistances;
    private Node edgeStartNode;
    private double tempEdgeX, tempEdgeY;

    public static final double NODE_RADIUS = 18;

    public CanvasPane() {
        canvas = new Canvas();
        getChildren().add(canvas);
        canvas.widthProperty().bind(this.widthProperty());
        canvas.heightProperty().bind(this.heightProperty());
        canvas.widthProperty().addListener(e -> draw());
        canvas.heightProperty().addListener(e -> draw());
    }

    public void setGraph(Graph graph) {
        this.graph = graph;
        resetVisualizationState();
    }

    public void setVisualizationState(Map<Node, String> nodeColors, Map<Edge, String> edgeColors, Map<Node, Double> distances) {
        this.nodeColors = nodeColors;
        this.edgeColors = edgeColors;
        this.nodeDistances = distances;
        draw();
    }

    public void setTempEdge(Node startNode, double endX, double endY) {
        this.edgeStartNode = startNode;
        this.tempEdgeX = endX;
        this.tempEdgeY = endY;
        draw();
    }
    
    public void clearTempEdge() {
        this.edgeStartNode = null;
        draw();
    }

    public void resetVisualizationState() {
        this.nodeColors = null;
        this.edgeColors = null;
        this.nodeDistances = null;
        draw();
    }

    public void draw() {
        if (graph == null) return;
        GraphicsContext gc = canvas.getGraphicsContext2D();
        gc.setFill(Color.web("#1e1e1e"));
        gc.fillRect(0, 0, canvas.getWidth(), canvas.getHeight());

        // Draw edges
        for (Edge edge : graph.getEdges()) {
            drawEdge(gc, edge);
        }
        
        // Draw temporary edge
        if (edgeStartNode != null) {
            gc.setStroke(Color.WHITE);
            gc.setLineDashes(10);
            gc.setLineWidth(2);
            gc.strokeLine(edgeStartNode.getX(), edgeStartNode.getY(), tempEdgeX, tempEdgeY);
            gc.setLineDashes(0);
        }

        // Draw nodes
        for (Node node : graph.getNodes()) {
            drawNode(gc, node);
        }
    }

    private void drawNode(GraphicsContext gc, Node node) {
        Color strokeColor = Color.web("#cccccc");
        Color fillColor = Color.web("#2d2d2d"); 

        if (nodeColors != null && nodeColors.containsKey(node)) {
            switch (nodeColors.get(node)) {
                case "visited": fillColor = Color.web("#c53939"); break;
                case "processing": fillColor = Color.web("#d6a213"); break;
                default: fillColor = Color.web("#333333"); break;
            }
        }

        gc.setStroke(strokeColor);
        gc.setLineWidth(3);
        gc.setFill(fillColor);
        
        gc.fillOval(node.getX() - NODE_RADIUS, node.getY() - NODE_RADIUS, 2 * NODE_RADIUS, 2 * NODE_RADIUS);
        gc.strokeOval(node.getX() - NODE_RADIUS, node.getY() - NODE_RADIUS, 2 * NODE_RADIUS, 2 * NODE_RADIUS);
        
        gc.setFill(Color.WHITE);
        gc.setFont(Font.font("Inter", FontWeight.BOLD, 14));
        gc.setTextAlign(TextAlignment.CENTER);
        gc.fillText(String.valueOf(node.getId()), node.getX(), node.getY() + 5);

        if (nodeDistances != null && nodeDistances.containsKey(node)) {
            double dist = nodeDistances.get(node);
            String distText = (dist == Double.MAX_VALUE) ? "\u221e" : String.format("%.0f", dist);
            gc.setFill(Color.AQUAMARINE);
            gc.setFont(Font.font("Inter", FontWeight.BOLD, 14));
            gc.fillText(distText, node.getX(), node.getY() + NODE_RADIUS + 18);
        }
    }

    private void drawEdge(GraphicsContext gc, Edge edge) {
        Color strokeColor = Color.web("#555");
        double lineWidth = 2.5;

        if (edgeColors != null && edgeColors.containsKey(edge)) {
            switch (edgeColors.get(edge)) {
                case "mst": strokeColor = Color.LIMEGREEN; lineWidth = 4; break;
                case "processing": strokeColor = Color.ORANGE; lineWidth = 3; break;
                case "discarded": strokeColor = Color.web("#660000"); lineWidth = 2; break;
            }
        }
        
        gc.setStroke(strokeColor);
        gc.setLineWidth(lineWidth);
        gc.strokeLine(edge.getStart().getX(), edge.getStart().getY(), edge.getEnd().getX(), edge.getEnd().getY());
    }
}
