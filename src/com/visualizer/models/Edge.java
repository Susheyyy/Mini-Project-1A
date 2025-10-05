package com.visualizer.models;

public class Edge implements Comparable<Edge> {
    private final Node start;
    private final Node end;
    private final double weight;

    public Edge(Node start, Node end) {
        this.start = start;
        this.end = end;
        // Weight is the Euclidean distance, scaled for display.
        this.weight = Math.round(Math.sqrt(Math.pow(start.getX() - end.getX(), 2) + Math.pow(start.getY() - end.getY(), 2)));
    }

    public Node getStart() { return start; }
    public Node getEnd() { return end; }
    public double getWeight() { return weight; }

    @Override
    public int compareTo(Edge other) {
        return Double.compare(this.weight, other.weight);
    }

    @Override
    public String toString() { return "Edge (" + start.getId() + " - " + end.getId() + ", w=" + weight + ")"; }
}
