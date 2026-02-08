/* global d3 */

const canvas = document.getElementById("neural-canvas");
const context = canvas.getContext("2d");

let width = canvas.clientWidth;
let height = canvas.clientHeight;
canvas.width = width;
canvas.height = height;

const zoom = d3.zoom().scaleExtent([0.3, 3]).on("zoom", (event) => {
  context.setTransform(event.transform.k, 0, 0, event.transform.k, event.transform.x, event.transform.y);
  render();
});

d3.select(canvas).call(zoom);

let nodes = [];
let links = [];
let agentRecommendation = null;
const particleSystem = window.ParticleSystem ? new window.ParticleSystem() : null;

function fetchData() {
  return fetch("/api/neural-data")
    .then((response) => response.json())
    .then((data) => {
      nodes = data.nodes;
      links = data.links;
      agentRecommendation = data.agent_recommendation;
      if (agentRecommendation && agentRecommendation.status === "recommended") {
        nodes = nodes.map((node) =>
          node.name === agentRecommendation.project
            ? { ...node, status: "recommended" }
            : node
        );
      }
      initSimulation();
    });
}

const simulation = d3
  .forceSimulation()
  .force("charge", d3.forceManyBody().strength(-400))
  .force("link", d3.forceLink().id((d) => d.id).strength((link) => link.strength))
  .force("center", d3.forceCenter(width / 2, height / 2));

function initSimulation() {
  simulation.nodes(nodes).on("tick", render);
  simulation
    .force("link")
    .links(links)
    .distance((link) => 60 + link.target.tier * 20);

  simulation.force("radial", d3.forceRadial((d) => 80 + d.tier * 40, width / 2, height / 2));
  simulation.alpha(1).restart();
}

function drawNode(node) {
  const radius = 12 + node.tier;
  context.shadowColor = "rgba(0, 234, 255, 0.6)";
  context.shadowBlur = node.status === "burning" ? 20 : 10;
  context.beginPath();
  context.arc(node.x, node.y, radius, 0, 2 * Math.PI);

  if (node.status === "burning") {
    context.fillStyle = "rgba(250, 204, 21, 0.95)";
  } else if (node.status === "recommended") {
    context.fillStyle = "rgba(0, 234, 255, 0.9)";
  } else if (node.status === "completed") {
    context.fillStyle = "rgba(34, 197, 94, 0.85)";
  } else if (node.status === "available") {
    context.fillStyle = "rgba(59, 130, 246, 0.8)";
  } else {
    context.fillStyle = "rgba(107, 114, 128, 0.6)";
  }

  context.fill();
  context.shadowBlur = 0;

  if (node.status === "recommended") {
    context.strokeStyle = "rgba(0, 234, 255, 0.8)";
    context.lineWidth = 2;
    context.strokeRect(node.x - radius - 6, node.y - radius - 6, radius * 2 + 12, radius * 2 + 12);
  }

  if (node.status === "burning" && particleSystem) {
    particleSystem.emit(node.x, node.y, 3);
  }
}

function render() {
  context.clearRect(0, 0, width, height);
  context.save();
  context.strokeStyle = "rgba(59, 130, 246, 0.4)";
  context.lineWidth = 1.2;
  links.forEach((link) => {
    context.beginPath();
    context.moveTo(link.source.x, link.source.y);
    context.lineTo(link.target.x, link.target.y);
    context.stroke();
  });
  links.forEach((link) => {
    const t = (Date.now() / 1000) % 1;
    const x = link.source.x + (link.target.x - link.source.x) * t;
    const y = link.source.y + (link.target.y - link.source.y) * t;
    context.fillStyle = "rgba(248, 250, 252, 0.8)";
    context.beginPath();
    context.arc(x, y, 2, 0, 2 * Math.PI);
    context.fill();
  });
  nodes.forEach(drawNode);
  if (particleSystem) {
    particleSystem.update();
    particleSystem.draw(context);
  }
  context.restore();
}

window.addEventListener("resize", () => {
  width = canvas.clientWidth;
  height = canvas.clientHeight;
  canvas.width = width;
  canvas.height = height;
  simulation.force("center", d3.forceCenter(width / 2, height / 2));
  simulation.alpha(0.5).restart();
});

fetchData();
