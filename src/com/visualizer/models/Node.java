package com.visualizer.models;

import javafx.beans.property.DoubleProperty;
import javafx.beans.property.SimpleDoubleProperty;

public class Node {
    private static int nextId = 0;
    private final int id;
    private final DoubleProperty x;
    private final DoubleProperty y;

    public Node(double x, double y) {
        this.id = nextId++;
        this.x = new SimpleDoubleProperty(x);
        this.y = new SimpleDoubleProperty(y);
    }

    public int getId() { return id; }
    public double getX() { return x.get(); }
    public void setX(double x) { this.x.set(x); }
    public double getY() { return y.get(); }
    public void setY(double y) { this.y.set(y); }

    @Override
    public String toString() { return "Node " + id; }

    public static void resetIdCounter() { nextId = 0; }
}
