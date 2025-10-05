package com.visualizer.controllers;

import com.visualizer.algorithms.*;
import com.visualizer.models.Graph;
import com.visualizer.models.Node;
import com.visualizer.ui.CanvasPane;
import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import javafx.scene.input.MouseButton;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.AnchorPane;
import javafx.util.Duration;
import java.util.List;

public class GraphController {

    @FXML private AnchorPane mainPane;
    @FXML private Button visualizeButton, clearButton;
    @FXML private ComboBox<String> algorithmComboBox, startNodeComboBox;
    @FXML private ListView<String> logListView;

    private CanvasPane canvasPane;
    private Graph graph;
    private Timeline timeline;
    private Node draggedNode, edgeStartNode;

    @FXML
    public void initialize() {
        graph = new Graph();
        canvasPane = new CanvasPane();
        mainPane.getChildren().add(canvasPane);
        AnchorPane.setTopAnchor(canvasPane, 0.0);
        AnchorPane.setBottomAnchor(canvasPane, 0.0);
        AnchorPane.setLeftAnchor(canvasPane, 0.0);
        AnchorPane.setRightAnchor(canvasPane, 0.0);

        canvasPane.setGraph(graph);
        canvasPane.setOnMousePressed(this::handleMousePressed);
        canvasPane.setOnMouseDragged(this::handleMouseDragged);
        canvasPane.setOnMouseReleased(this::handleMouseReleased);
        canvasPane.setOnMouseMoved(this::handleMouseMoved);

        timeline = new Timeline();
        timeline.setOnFinished(e -> setControlsDisabled(false));

        algorithmComboBox.getItems().addAll("Dijkstra", "Bellman-Ford", "Prim's", "Kruskal's");
        algorithmComboBox.getSelectionModel().selectFirst();
        
        visualizeButton.setOnAction(e -> runAlgorithm());
        clearButton.setOnAction(e -> resetGraph());
    }
    
    private void handleMousePressed(MouseEvent e) {
        if (timeline.getStatus() == Timeline.Status.RUNNING) return;
        Node clickedNode = findNodeAt(e.getX(), e.getY());
        if (e.getButton() == MouseButton.PRIMARY && clickedNode != null) draggedNode = clickedNode;
        else if (e.getButton() == MouseButton.SECONDARY && clickedNode != null) edgeStartNode = clickedNode;
    }

    private void handleMouseDragged(MouseEvent e) {
        if (draggedNode != null) {
            draggedNode.setX(e.getX());
            draggedNode.setY(e.getY());
            canvasPane.draw();
        } else if (edgeStartNode != null) {
            canvasPane.setTempEdge(edgeStartNode, e.getX(), e.getY());
        }
    }

    private void handleMouseReleased(MouseEvent e) {
         if (draggedNode != null) draggedNode = null;
         else if (edgeStartNode != null) {
            Node endNode = findNodeAt(e.getX(), e.getY());
            if (endNode != null && !endNode.equals(edgeStartNode)) graph.addEdge(edgeStartNode, endNode);
            edgeStartNode = null;
            canvasPane.clearTempEdge();
         } else if (e.getButton() == MouseButton.PRIMARY && findNodeAt(e.getX(), e.getY()) == null) {
            graph.addNode(new Node(e.getX(), e.getY()));
            updateComboBoxes();
            canvasPane.draw();
         }
    }
    
    private void handleMouseMoved(MouseEvent e) {
        if (edgeStartNode != null) canvasPane.setTempEdge(edgeStartNode, e.getX(), e.getY());
    }

    private void runAlgorithm() {
        String selectedAlgo = algorithmComboBox.getValue();
        Node startNode = getSelectedNode(startNodeComboBox);
        
        boolean requiresStartNode = selectedAlgo.equals("Dijkstra") || selectedAlgo.equals("Bellman-Ford") || selectedAlgo.equals("Prim's");
        if (requiresStartNode && startNode == null) {
            showAlert("Error", "Please select a start node for this algorithm.");
            return;
        }

        List<AlgorithmStep> steps;
        switch(selectedAlgo) {
            case "Dijkstra": steps = Dijkstra.run(graph, startNode); break;
            case "Bellman-Ford": steps = BellmanFord.run(graph, startNode); break;
            case "Prim's": steps = Prim.run(graph, startNode); break;
            case "Kruskal's": steps = Kruskal.run(graph); break;
            default: return;
        }
        animate(steps);
    }
    
    private void animate(List<AlgorithmStep> steps) {
        timeline.stop();
        timeline.getKeyFrames().clear();
        logListView.getItems().clear();
        canvasPane.resetVisualizationState();
        setControlsDisabled(true);

        Duration frameTime = Duration.ZERO;
        Duration delay = Duration.millis(600);

        for (AlgorithmStep step : steps) {
            frameTime = frameTime.add(delay);
            KeyFrame kf = new KeyFrame(frameTime, e -> {
                canvasPane.setVisualizationState(step.nodeColors, step.edgeColors, step.nodeDistances);
                logListView.getItems().add(step.logMessage);
                logListView.scrollTo(logListView.getItems().size() - 1);
            });
            timeline.getKeyFrames().add(kf);
        }
        timeline.play();
    }

    private void resetGraph() {
        timeline.stop();
        graph.clear();
        canvasPane.resetVisualizationState();
        logListView.getItems().clear();
        updateComboBoxes();
        startNodeComboBox.getSelectionModel().clearSelection();
        edgeStartNode = draggedNode = null;
        setControlsDisabled(false);
    }
    
    private void setControlsDisabled(boolean disabled) {
        visualizeButton.setDisable(disabled);
        clearButton.setDisable(disabled);
        algorithmComboBox.setDisable(disabled);
        startNodeComboBox.setDisable(disabled);
    }

    private void updateComboBoxes() {
        String selectedStart = startNodeComboBox.getValue();
        startNodeComboBox.getItems().clear();
        for (Node node : graph.getNodes()) startNodeComboBox.getItems().add("Node " + node.getId());
        startNodeComboBox.setValue(selectedStart);
    }
    
    private Node findNodeAt(double x, double y) {
        return graph.getNodes().stream()
                .filter(node -> Math.pow(node.getX() - x, 2) + Math.pow(node.getY() - y, 2) <= Math.pow(CanvasPane.NODE_RADIUS, 2))
                .findFirst().orElse(null);
    }
    
    private Node getSelectedNode(ComboBox<String> comboBox) {
        String selected = comboBox.getSelectionModel().getSelectedItem();
        if (selected == null) return null;
        try {
            int nodeId = Integer.parseInt(selected.split(" ")[1]);
            return graph.getNodes().stream().filter(n -> n.getId() == nodeId).findFirst().orElse(null);
        } catch (Exception e) { return null; }
    }
    
    private void showAlert(String title, String message) {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.showAndWait();
    }
}
