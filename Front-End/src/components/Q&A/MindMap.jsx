// MindMap.jsx
import React, { useState, useMemo } from "react";
import { Graph } from "react-d3-graph";

const MindMap = ({ data }) => {
  const [selectedTopic, setSelectedTopic] = useState("All");

  const topics = useMemo(() => {
    return data.nodes
      .filter((n) => n.id.startsWith("Topic:"))
      .map((n) => n.label);
  }, [data]);

  const filteredData = useMemo(() => {
    const validNodeIds = new Set();
    const filteredNodes = [];
    const filteredLinks = [];

    const centerNode = data.nodes.find((n) => n.id === "Weak Areas");
    if (centerNode) {
      filteredNodes.push(centerNode);
      validNodeIds.add(centerNode.id);
    }

    const topicNodes = data.nodes.filter((n) => n.id.startsWith("Topic:"));

    topicNodes.forEach((topic) => {
      const includeTopic = selectedTopic === "All" || topic.label === selectedTopic;
      if (includeTopic && !validNodeIds.has(topic.id)) {
        filteredNodes.push(topic);
        validNodeIds.add(topic.id);

        const subLinks = data.links.filter((l) => l.source === topic.id);
        subLinks.forEach((link) => {
          const targetNode = data.nodes.find((n) => n.id === link.target);
          if (targetNode && !validNodeIds.has(targetNode.id)) {
            filteredNodes.push(targetNode);
            validNodeIds.add(targetNode.id);
          }
          filteredLinks.push(link);
        });

        filteredLinks.push({ source: "Weak Areas", target: topic.id });
      }
    });

    return {
      nodes: filteredNodes,
      links: filteredLinks,
    };
  }, [data, selectedTopic]);

  const config = {
    directed: true,
    height: 600,
    width: 1000,
    nodeHighlightBehavior: true,
    node: {
      color: "lightgray",
      fontSize: 14,
      highlightStrokeColor: "blue",
      labelProperty: "label",
      size: 400,
    },
    link: {
      highlightColor: "gray",
    },
    panAndZoom: true,
    staticGraph: false,
    draggable: true,
    focusAnimationDuration: 0.75,
    layout: {
      hierarchical: true,
      direction: "TB",
      sortMethod: "directed",
    },
    d3: {
      gravity: -300,
      linkLength: 120,
      alphaTarget: 0.05,
    },
  };

  const enhancedNodes = filteredData.nodes.map((node) => {
    let color = "#facc15";
    if (node.id === "Weak Areas") color = "#f472b6";
    else if (node.id.startsWith("Topic:Molecular Biology")) color = "#60a5fa";
    else if (node.id.startsWith("Topic:Evolution")) color = "#a78bfa";
    else if (node.id.startsWith("Topic:Introduction")) color = "#34d399";
    return { ...node, color };
  });

  return (
    <div>
      <div className="mb-4">
        <label className="mr-2 font-semibold text-sm">Filter by Topic:</label>
        <select
          value={selectedTopic}
          onChange={(e) => setSelectedTopic(e.target.value)}
          className="border px-2 py-1 rounded text-sm"
        >
          <option value="All">All</option>
          {topics.map((topic) => (
            <option key={topic} value={topic}>
              {topic}
            </option>
          ))}
        </select>
      </div>

      <div className="overflow-x-auto border rounded-md p-2 bg-white shadow-md">
        <Graph
          id="student-mind-map"
          data={{ nodes: enhancedNodes, links: filteredData.links }}
          config={config}
        />
      </div>
    </div>
  );
};

export default MindMap;
