// script.js - FIXED Weight Input Version
document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const algoInfoBox = document.getElementById('algo-info-box');
    const generateInputsBtn = document.getElementById('generate-inputs-btn');
    const drawGraphBtn = document.getElementById('draw-graph-btn');
    const runAlgoBtn = document.getElementById('run-algo-btn');
    const prevStepBtn = document.getElementById('prev-step-btn');
    const nextStepBtn = document.getElementById('next-step-btn');
    const resetBtn = document.getElementById('reset-btn');
    const timelineSlider = document.getElementById('timeline-slider');
    const algorithmSelect = document.getElementById('algorithm-select');
    const startNodeGroup = document.getElementById('start-node-group');
    const svg = document.getElementById('graph-svg');
    const messageBox = document.getElementById('message-box');
    const stepCounter = document.getElementById('step-counter');

    // --- State & Mappings ---
    let graphData = { nodes: [], edges: [] };
    let visualizationSteps = [];
    let currentStep = 0;
    let nodeLetterToId = {};
    let nodeIdToLetter = {};
    
    // --- Constants ---
    const API_URL = '/api/run_algorithm';
   const ALGO_DESCRIPTIONS = {
        'dijkstra': {
            name: "Dijkstra's Algorithm",
            desc: "Finds the shortest path from a starting node to all other nodes in a weighted graph. Works with non-negative edge weights only.",
            complexity: "Time: O(E log V) | Space: O(V)"
        },
        'bellman-ford': {
            name: "Bellman-Ford Algorithm",
            desc: "Finds the shortest paths from a single source. Slower than Dijkstra's but can handle negative edge weights and detect negative cycles.",
            complexity: "Time: O(V × E) | Space: O(V)"
        },
        'kruskal': {
            name: "Kruskal's Algorithm",
            desc: "Finds a Minimum Spanning Tree (MST) for a weighted, undirected graph. Sorts all edges and adds them to the MST if they don't form a cycle.",
            complexity: "Time: O(E log E) | Space: O(V + E)"
        },
        'prim': {
            name: "Prim's Algorithm",
            desc: "Finds a Minimum Spanning Tree (MST). Starts from an arbitrary node and grows the MST by adding the cheapest connection from a known to an unknown vertex.",
            complexity: "Time: O(E log V) | Space: O(V + E)"
        }
    }; 

    // --- Event Listeners ---
    algorithmSelect.addEventListener('change', updateAlgorithmInfo);
    generateInputsBtn.addEventListener('click', generateEdgeInputs);
    drawGraphBtn.addEventListener('click', drawGraph);
    runAlgoBtn.addEventListener('click', runAlgorithm);
    prevStepBtn.addEventListener('click', () => updateVisualization(currentStep - 1));
    nextStepBtn.addEventListener('click', () => updateVisualization(currentStep + 1));
    resetBtn.addEventListener('click', () => {
        if (graphData.nodes.length > 0) {
            drawGraph();
            setVisualizationControls(false);
            visualizationSteps = [];
            currentStep = 0;
            messageBox.textContent = "Visualization reset. Run an algorithm to start.";
        }
    });
    timelineSlider.addEventListener('input', (e) => updateVisualization(parseInt(e.target.value)));

    // --- Core Functions ---
    
    function setupNodeMappings(numVertices) {
        nodeLetterToId = {};
        nodeIdToLetter = {};
        for (let i = 0; i < numVertices; i++) {
            const letter = String.fromCharCode(65 + i); // A, B, C...
            nodeLetterToId[letter] = i;
            nodeIdToLetter[i] = letter;
        }
    }

    function updateAlgorithmInfo() {
        const selectedAlgo = algorithmSelect.value;
        const info = ALGO_DESCRIPTIONS[selectedAlgo];
        const needsStartNode = ['dijkstra', 'bellman-ford'].includes(selectedAlgo);
        
        startNodeGroup.style.display = needsStartNode ? 'flex' : 'none';
        
        algoInfoBox.innerHTML = `
            <h3>${info.name}</h3>
            <p>${info.desc}</p>
            <code>${info.complexity}</code>
        `;
    }

    function generateEdgeInputs() {
        const numVertices = parseInt(document.getElementById('vertices').value);
        
        if (numVertices < 2 || numVertices > 26) {
            messageBox.textContent = "Error: Please enter between 2 and 26 nodes.";
            return;
        }
        
        setupNodeMappings(numVertices);

        const numEdges = parseInt(document.getElementById('edges').value);
        
        if (numEdges < 1 || numEdges > 50) {
            messageBox.textContent = "Error: Please enter between 1 and 50 edges.";
            return;
        }
        
        const container = document.getElementById('edge-inputs-container');
        container.innerHTML = '';

        for (let i = 0; i < numEdges; i++) {
            const row = document.createElement('div');
            row.className = 'edge-input-row';

            const span = document.createElement('span');
            span.textContent = `E${i + 1}:`;

            const fromInput = document.createElement('input');
            fromInput.type = 'text';
            fromInput.placeholder = 'From';
            fromInput.className = 'edge-from';
            fromInput.maxLength = 1;
            fromInput.addEventListener('input', function() {
                this.value = this.value.toUpperCase();
            });

            const toInput = document.createElement('input');
            toInput.type = 'text';
            toInput.placeholder = 'To';
            toInput.className = 'edge-to';
            toInput.maxLength = 1;
            toInput.addEventListener('input', function() {
                this.value = this.value.toUpperCase();
            });
            
            const weightInput = document.createElement('input');
            weightInput.type = 'number';
            weightInput.placeholder = 'Weight';
            weightInput.className = 'edge-weight';
            weightInput.setAttribute('min', '1');
            weightInput.setAttribute('step', '1');
            weightInput.value = ''; // Explicitly set to empty

            row.append(span, fromInput, toInput, weightInput);
            container.appendChild(row);
        }
        
        drawGraphBtn.disabled = false;
        messageBox.textContent = "Edge inputs generated. Fill in node letters (A, B, C...) and weights, then click 'Generate Graph'.";
    }

    function drawGraph() {
        svg.innerHTML = '';
        const numVertices = parseInt(document.getElementById('vertices').value);
        setupNodeMappings(numVertices);
        const edgeInputRows = document.querySelectorAll('.edge-input-row');

        graphData.nodes = Array.from({ length: numVertices }, (_, i) => ({ id: i }));
        graphData.edges = [];
        
        let isValid = true;
        let errorMessage = "";
        
        edgeInputRows.forEach((row, index) => {
            const fromLetter = row.querySelector('.edge-from').value.trim().toUpperCase();
            const toLetter = row.querySelector('.edge-to').value.trim().toUpperCase();
            const weightValue = row.querySelector('.edge-weight').value.trim();
            
            // Check if fields are empty
            if (!fromLetter || !toLetter || !weightValue) {
                isValid = false;
                errorMessage = `Error: Edge ${index + 1} has empty fields. Please fill in all fields (From, To, Weight).`;
                return;
            }
            
            const weight = parseInt(weightValue);
            const fromId = nodeLetterToId[fromLetter];
            const toId = nodeLetterToId[toLetter];

            if (fromId === undefined || toId === undefined) {
                isValid = false;
                errorMessage = `Error: Invalid node letter in edge ${index + 1}. Use letters A-${String.fromCharCode(64 + numVertices)}.`;
            } else if (isNaN(weight) || weight <= 0) {
                isValid = false;
                errorMessage = `Error: Invalid weight in edge ${index + 1}. Weight must be a positive integer (you entered: "${weightValue}").`;
            } else if (fromId === toId) {
                isValid = false;
                errorMessage = `Error: Self-loop detected in edge ${index + 1}. From and To nodes cannot be the same.`;
            } else {
                graphData.edges.push([fromId, toId, weight]);
            }
        });
        
        if (!isValid) {
            messageBox.textContent = errorMessage;
            runAlgoBtn.disabled = true;
            svg.innerHTML = '';
            return;
        }

        const { width, height } = svg.getBoundingClientRect();
        const radius = Math.min(width, height) * 0.38;
        const centerX = width / 2;
        const centerY = height / 2;

        graphData.nodes.forEach((node, i) => {
            const angle = (i / numVertices) * 2 * Math.PI - Math.PI / 2;
            node.x = centerX + radius * Math.cos(angle);
            node.y = centerY + radius * Math.sin(angle);
        });

        const edgeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        graphData.edges.forEach(([u, v, w]) => {
            const edgeId = `edge-${Math.min(u, v)}-${Math.max(u, v)}`;
            const n1 = graphData.nodes[u];
            const n2 = graphData.nodes[v];

            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', n1.x);
            line.setAttribute('y1', n1.y);
            line.setAttribute('x2', n2.x);
            line.setAttribute('y2', n2.y);
            line.setAttribute('id', edgeId);
            line.setAttribute('class', 'edge');
            edgeGroup.appendChild(line);

            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', (n1.x + n2.x) / 2);
            text.setAttribute('y', (n1.y + n2.y) / 2 - 8);
            text.setAttribute('class', 'edge-weight');
            text.textContent = w;
            edgeGroup.appendChild(text);
        });
        svg.appendChild(edgeGroup);
        
        const nodeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        graphData.nodes.forEach(node => {
            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            g.setAttribute('class', 'node'); 
            g.setAttribute('id', `node-${node.id}`);

            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', node.x);
            circle.setAttribute('cy', node.y);
            circle.setAttribute('r', 24);
            circle.style.fill = "#60a5fa";
            
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', node.x);
            text.setAttribute('y', node.y + 6);
            text.textContent = nodeIdToLetter[node.id];
            
            const infoText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            infoText.setAttribute('x', node.x);
            infoText.setAttribute('y', node.y - 32);
            infoText.setAttribute('class', 'node-info-text');
            infoText.setAttribute('id', `info-text-${node.id}`);

            g.append(circle, text, infoText);
            nodeGroup.appendChild(g);
        });
        svg.appendChild(nodeGroup);

        runAlgoBtn.disabled = false;
        messageBox.textContent = `Graph generated successfully with ${graphData.edges.length} edges! Select an algorithm and click 'Run Algorithm'.`;
        
        // Log the graph data for debugging
        console.log('Graph Data:', graphData);
    }

    async function runAlgorithm() {
        const algorithm = algorithmSelect.value;
        const startNodeLetter = document.getElementById('start-node').value.toUpperCase();
        const startNodeId = nodeLetterToId[startNodeLetter];

        if (startNodeId === undefined && ['dijkstra', 'bellman-ford'].includes(algorithm)) {
            const maxLetter = String.fromCharCode(64 + graphData.nodes.length);
            messageBox.textContent = `Error: Please enter a valid start node (A-${maxLetter}).`;
            return;
        }
        
        const payload = {
            algorithm: algorithm,
            graph: {
                nodes: graphData.nodes.map(n => n.id),
                edges: graphData.edges,
                startNode: startNodeId
            }
        };

        console.log('Sending to server:', payload);

        try {
            messageBox.textContent = `Running ${ALGO_DESCRIPTIONS[algorithm].name}...`;
            runAlgoBtn.disabled = true;
            
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            console.log('Response status:', response.status);
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error('Server error:', errorData);
                throw new Error(`Server error: ${errorData.error || response.statusText}`);
            }
            
            visualizationSteps = await response.json();
            console.log('Received steps:', visualizationSteps.length);
            
            if (visualizationSteps.length > 0 && !visualizationSteps.error) {
                currentStep = 0;
                setVisualizationControls(true);
                timelineSlider.max = visualizationSteps.length - 1;
                updateVisualization(0);
            } else {
                messageBox.textContent = "Algorithm produced no steps or an error occurred.";
            }

        } catch (error) {
            console.error("Full error details:", error);
            messageBox.textContent = `Error: ${error.message}. Check console for details.`;
        } finally {
            runAlgoBtn.disabled = false;
        }
    }

    function updateVisualization(stepIndex) {
        if (stepIndex < 0 || stepIndex >= visualizationSteps.length) return;
        currentStep = stepIndex;
        const stepData = visualizationSteps[currentStep];

        Object.entries(stepData.nodes).forEach(([nodeId, state]) => {
            const nodeG = document.getElementById(`node-${nodeId}`);
            if (nodeG) {
                nodeG.querySelector('circle').style.fill = state.color;
                nodeG.querySelector('.node-info-text').textContent = state.text;
            }
        });
        
        Object.entries(stepData.edges).forEach(([edgeId, state]) => {
            const edgeLine = document.getElementById(`edge-${edgeId}`);
            if (edgeLine) {
                edgeLine.style.stroke = state.color;
                edgeLine.style.strokeWidth = state.width + 'px';
            }
        });
        
        messageBox.textContent = stepData.message;
        timelineSlider.value = currentStep;
        stepCounter.textContent = `Step ${currentStep} / ${visualizationSteps.length - 1}`;
        
        prevStepBtn.disabled = currentStep === 0;
        nextStepBtn.disabled = currentStep === visualizationSteps.length - 1;
    }
    
    function setVisualizationControls(isEnabled) {
        prevStepBtn.disabled = !isEnabled;
        nextStepBtn.disabled = !isEnabled;
        resetBtn.disabled = !isEnabled;
        timelineSlider.disabled = !isEnabled;
        
        if (isEnabled) {
            prevStepBtn.disabled = true;
        } else {
            timelineSlider.value = 0;
            stepCounter.textContent = 'Step 0 / 0';
        }
    }

    // --- Initial Page Load ---
    updateAlgorithmInfo();
    messageBox.textContent = "Welcome! Set the number of nodes and edges, then click 'Define Edges' to begin.";
});