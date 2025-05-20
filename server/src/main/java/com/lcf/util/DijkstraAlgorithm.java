package com.lcf.util;

import java.util.*;

public class DijkstraAlgorithm {
    public static List<Integer> dijkstra(int[][] graph, int start) {
        int n = graph.length;
        int[] distances = new int[n];
        boolean[] visited = new boolean[n];
        Arrays.fill(distances, Integer.MAX_VALUE);
        distances[start] = 0;

        PriorityQueue<int[]> pq = new PriorityQueue<>(Comparator.comparingInt(a -> a[1]));
        pq.add(new int[]{start, 0});

        while (!pq.isEmpty()) {
            int[] current = pq.poll();
            int currentNode = current[0];
            int currentDistance = current[1];

            if (visited[currentNode]) continue;
            visited[currentNode] = true;

            for (int neighbor = 0; neighbor < n; neighbor++) {
                if (graph[currentNode][neighbor] > 0 && !visited[neighbor]) {
                    int newDistance = currentDistance + graph[currentNode][neighbor];
                    if (newDistance < distances[neighbor]) {
                        distances[neighbor] = newDistance;
                        pq.add(new int[]{neighbor, newDistance});
                    }
                }
            }
        }

        // Reconstruct the path
        List<Integer> path = new ArrayList<>();
        int current = start;
        while (current != -1) {
            path.add(current);
            int minDistance = Integer.MAX_VALUE;
            int nextNode = -1;
            for (int neighbor = 0; neighbor < n; neighbor++) {
                if (graph[current][neighbor] > 0 && distances[neighbor] < minDistance) {
                    minDistance = distances[neighbor];
                    nextNode = neighbor;
                }
            }
            current = nextNode;
        }
        Collections.reverse(path);
        return path;
    }
}
