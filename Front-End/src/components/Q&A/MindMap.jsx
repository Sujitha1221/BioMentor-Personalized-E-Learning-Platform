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

  const colorPalette = [
    "#60a5fa", // blue
    "#a78bfa", // purple
    "#34d399", // green
    "#f87171", // red
    "#fbbf24", // amber
    "#38bdf8", // sky
    "#f472b6", // pink
    "#c084fc", // violet
    "#4ade80", // emerald
    "#facc15", // yellow
  ];

  // Map topic label to a color index
  const topicColorMap = {};
  let colorIndex = 0;

  data.nodes.forEach((node) => {
    if (node.id.startsWith("Topic:")) {
      const label = node.label;
      if (!topicColorMap[label]) {
        topicColorMap[label] = colorPalette[colorIndex % colorPalette.length];
        colorIndex++;
      }
    }
  });

  // Optional: Fallback hash-based color generator
  const stringToColor = (str) => {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const color = '#' + ((hash >> 24) & 0xFF).toString(16).padStart(2, '0') +
      ((hash >> 16) & 0xFF).toString(16).padStart(2, '0') +
      ((hash >> 8) & 0xFF).toString(16).padStart(2, '0');
    return color;
  };

  const enhancedNodes = filteredData.nodes.map((node) => {
    let color = "#facc15"; // default
    if (node.id === "Weak Areas") {
      color = "#f472b6";
    } else if (node.id.startsWith("Topic:")) {
      color = topicColorMap[node.label] || stringToColor(node.label);
    }
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
