"""
Graph visualizer for requirement decomposition.

Creates an interactive HTML visualization of the requirement graph
for demonstration purposes.
"""

import asyncio
from pathlib import Path
from uuid import UUID
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

import plotly.graph_objects as go
import networkx as nx
from src.agents.requirement_decomposer import RequirementDecomposerAgent
from src.models.hypothesis import Hypothesis


def create_graph_visualization(graph, output_path: str = "requirement_graph.html"):
    """
    Create an interactive visualization of the requirement graph.

    Args:
        graph: RequirementGraph to visualize
        output_path: Path to save the HTML file
    """
    # Create NetworkX graph
    G = nx.DiGraph()

    # Store full content for nodes
    node_full_content = {}

    # Add all nodes
    for node_id, node in graph.nodes.items():
        node_id_str = str(node_id)
        G.add_node(
            node_id_str,
            content=node.content,
            level=node.level,
            is_shared=node.is_shared,
            is_atomic=len(graph.children_map.get(node_id, [])) == 0,
        )
        node_full_content[node_id_str] = node.content

    # Add all edges (parent -> child relationships)
    for parent_id, children_ids in graph.children_map.items():
        for child_id in children_ids:
            G.add_edge(str(parent_id), str(child_id))

    # Create hierarchical layout with parent-child blocks
    pos = {}
    node_order = {}  # Track ordering of nodes at each level

    # Find root node
    root_id = str(graph.root_id)

    # Position root at center
    pos[root_id] = (0, 0)
    node_order[0] = [root_id]

    # Track which nodes have been positioned (for shared nodes)
    positioned = {root_id}

    # Process each level
    max_level = max(node.level for node in graph.nodes.values())
    for level in range(max_level):
        current_level_nodes = node_order.get(level, [])
        if not current_level_nodes:
            continue

        # Group children by parent
        parent_blocks = []
        for parent_id_str in current_level_nodes:
            # Convert string back to UUID to look up in graph
            parent_uuid = UUID(parent_id_str)

            # Get children from the children_map
            children_ids = [str(cid) for cid in graph.children_map.get(parent_uuid, [])]

            # Filter to only include children not yet positioned (handle shared nodes)
            new_children = []
            for child_id in children_ids:
                if child_id not in positioned:
                    new_children.append(child_id)
                    positioned.add(child_id)

            if new_children:
                parent_blocks.append({
                    'parent_id': parent_id_str,
                    'children': new_children
                })

        if not parent_blocks:
            continue

        # Position children in blocks under parents
        y = -(level + 1) * 1.5
        next_level_order = []

        # Track the rightmost x position used to avoid overlaps
        rightmost_x = None

        # First pass: calculate total width needed
        total_width = sum(len(block['children']) for block in parent_blocks)

        # Level-dependent spacing: more spacing for parent nodes, less for leaf nodes
        # Early levels (0, 1, 2) get more spacing
        child_level = level + 1
        if child_level <= 2:
            spacing = 5.0  # Larger spacing for upper levels
            block_gap = 1.2  # More gap between blocks
        else:
            spacing = 1.2  # Current spacing for lower levels (leaves)
            block_gap = 0.8  # Current gap for lower levels

        # Start from leftmost position
        if parent_blocks:
            # Center the entire level under the parents
            leftmost_parent = min(pos[block['parent_id']][0] for block in parent_blocks)
            rightmost_parent = max(pos[block['parent_id']][0] for block in parent_blocks)
            level_center = (leftmost_parent + rightmost_parent) / 2
            level_width = (total_width - 1) * spacing + (len(parent_blocks) - 1) * block_gap
            current_x = level_center - level_width / 2

        for i, block in enumerate(parent_blocks):
            parent_id = block['parent_id']
            children = block['children']
            num_children = len(children)

            # Position this block starting from current_x
            for j, child_id in enumerate(children):
                child_x = current_x + j * spacing
                pos[child_id] = (child_x, y)
                next_level_order.append(child_id)

            # Move current_x to after this block, with gap before next block
            current_x += num_children * spacing
            if i < len(parent_blocks) - 1:  # Add gap between blocks (not after last)
                current_x += block_gap

        # Store ordering for next level
        if next_level_order:
            node_order[level + 1] = next_level_order

    # Add any remaining nodes that weren't positioned (edge case)
    for node_id_str in G.nodes():
        if node_id_str not in pos:
            node_level = G.nodes[node_id_str]['level']
            pos[node_id_str] = (0, -node_level * 1.5)

    # Create arrow annotations for edges
    edge_annotations = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]

        # Calculate arrow position (midpoint closer to child)
        arrow_x = x0 * 0.3 + x1 * 0.7
        arrow_y = y0 * 0.3 + y1 * 0.7

        edge_annotations.append(
            dict(
                x=x1,
                y=y1,
                ax=x0,
                ay=y0,
                xref='x',
                yref='y',
                axref='x',
                ayref='y',
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=1.5,
                arrowcolor='#888',
                opacity=0.6,
            )
        )

    # Create edge traces (lines without arrows, arrows added separately)
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1.5, color="#888"),
        hoverinfo="none",
        mode="lines",
        showlegend=False,
    )

    # Create nodes
    node_x = []
    node_y = []
    node_label = []  # Short labels to display on nodes
    node_hover = []  # Full content on hover
    node_color = []
    node_size = []

    for node_id in G.nodes():
        x, y = pos[node_id]
        node_x.append(x)
        node_y.append(y)

        node_data = G.nodes[node_id]
        content = node_data["content"]
        level = node_data["level"]
        is_shared = node_data["is_shared"]
        is_atomic = node_data["is_atomic"]

        # Show only first 10 characters on node
        label = content[:10] + "..." if len(content) > 10 else content

        # Full content on hover
        hover_text = f"<b>{content}</b><br>"
        hover_text += f"Level: {level}<br>"
        if is_shared:
            hover_text += "🔗 SHARED NODE<br>"
        if is_atomic:
            hover_text += "🎯 ATOMIC<br>"

        node_label.append(label)
        node_hover.append(hover_text)

        # Color scheme: red for all nodes, orange for shared
        if is_shared:
            node_color.append("#FFA500")  # Orange for shared
            node_size.append(20)
        else:
            node_color.append("#ff2d55")  # Red for all other nodes
            if level == 0:
                node_size.append(25)  # Larger root
            else:
                node_size.append(18)

    # Store full content for click display
    node_full_text = []
    for node_id in G.nodes():
        node_data = G.nodes[node_id]
        node_full_text.append(node_data["content"])

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",  # Only markers, no text labels
        hoverinfo="text",
        hovertext=node_hover,  # Full text on hover
        marker=dict(
            showscale=False,
            color=node_color,
            size=node_size,
            line=dict(width=2, color="white"),
        ),
        customdata=node_full_text,  # Store full content for click events
        showlegend=False,
    )

    # Combine edge arrows and legend annotation
    all_annotations = edge_annotations + [
        dict(
            text="Legend: 🔴 Regular Node | 🟠 Shared Node",
            showarrow=False,
            xref="paper",
            yref="paper",
            x=0.5,
            y=-0.05,
            xanchor="center",
            yanchor="top",
            font=dict(size=12),
        )
    ]

    # Create figure
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(
                text=f"<b>Requirement Decomposition Graph</b><br>"
                     f"<sub>Total: {graph.total_nodes} nodes | "
                     f"Atomic: {graph.atomic_count} | "
                     f"Shared: {graph.shared_count} | "
                     f"Depth: {graph.max_depth}</sub>",
                x=0.5,
                xanchor="center",
                font=dict(size=20),
            ),
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=80),
            annotations=all_annotations,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="white",
            height=800,
        ),
    )

    # Save to HTML with custom JavaScript for click handling
    output_file = ROOT_DIR / output_path

    # Custom JavaScript to handle node clicks
    custom_js = """
    <script>
    // Wait for plot to be ready
    setTimeout(function() {
        var myPlot = document.getElementsByClassName('plotly-graph-div')[0];
        var clickedNodes = new Set();
        var baseAnnotationCount = myPlot.layout.annotations.length;

        console.log('Click handler initialized');

        myPlot.on('plotly_click', function(data){
            console.log('Node clicked!', data);

            if (!data.points || data.points.length === 0) return;

            var point = data.points[0];
            var content = point.customdata;
            var x = point.x;
            var y = point.y;
            var pointIndex = point.pointIndex;

            console.log('Content:', content);

            // Check if this node is already showing
            if (clickedNodes.has(pointIndex)) {
                console.log('Node already showing, skipping');
                return;
            }

            // Mark this node as showing
            clickedNodes.add(pointIndex);

            // Add new annotation with full content
            var newAnnotation = {
                x: x,
                y: y,
                xref: 'x',
                yref: 'y',
                text: content,
                showarrow: true,
                arrowhead: 2,
                arrowsize: 1,
                arrowwidth: 2,
                arrowcolor: '#333',
                ax: 0,
                ay: -70,
                bgcolor: 'rgba(255, 255, 255, 0.95)',
                bordercolor: '#ff2d55',
                borderwidth: 2,
                borderpad: 10,
                font: {
                    size: 11,
                    color: '#333'
                },
                align: 'left',
                xanchor: 'center',
                yanchor: 'bottom',
                captureevents: true,
                clicktoshow: false
            };

            var currentAnnotations = myPlot.layout.annotations.slice();
            currentAnnotations.push(newAnnotation);

            Plotly.relayout(myPlot, {
                'annotations': currentAnnotations
            }).then(function() {
                console.log('Annotation added successfully');
            });
        });

        // Add a button to clear all labels
        var clearButton = document.createElement('button');
        clearButton.innerHTML = 'Clear All Labels';
        clearButton.style.position = 'absolute';
        clearButton.style.top = '10px';
        clearButton.style.right = '10px';
        clearButton.style.zIndex = '1000';
        clearButton.style.padding = '8px 16px';
        clearButton.style.backgroundColor = '#ff2d55';
        clearButton.style.color = 'white';
        clearButton.style.border = 'none';
        clearButton.style.borderRadius = '4px';
        clearButton.style.cursor = 'pointer';
        clearButton.style.fontWeight = 'bold';
        clearButton.style.fontSize = '12px';

        clearButton.onclick = function() {
            // Reset to base annotations (arrows only)
            var baseAnnotations = myPlot.layout.annotations.slice(0, baseAnnotationCount);
            Plotly.relayout(myPlot, {
                'annotations': baseAnnotations
            });
            clickedNodes.clear();
            console.log('All labels cleared');
        };

        myPlot.parentNode.style.position = 'relative';
        myPlot.parentNode.appendChild(clearButton);

    }, 500);
    </script>
    """

    # Write HTML with custom JavaScript
    html_string = fig.to_html(include_plotlyjs='cdn')
    html_string = html_string.replace('</body>', custom_js + '</body>')

    with open(output_file, 'w') as f:
        f.write(html_string)

    print(f"\n✅ Visualization saved to: {output_file}")
    print(f"   Open in browser to view the interactive graph!")
    print(f"   Click on nodes to show full content (labels persist)")
    print(f"   Use 'Clear All Labels' button to reset")

    return output_file


def load_and_visualize(input_path: str, output_path: str = "requirement_graph.html"):
    """
    Load a saved graph and create visualization.

    Args:
        input_path: Path to saved graph JSON file
        output_path: Path to save the HTML visualization
    """
    from src.models.requirement import RequirementGraph

    print(f"📂 Loading graph from: {input_path}")
    graph = RequirementGraph.load_from_file(input_path)

    print(f"\n📊 Graph Statistics:")
    print(f"   Total nodes: {graph.total_nodes}")
    print(f"   Max depth: {graph.max_depth}")
    print(f"   Atomic nodes: {graph.atomic_count}")
    print(f"   Shared nodes: {graph.shared_count}")

    # Create visualization
    output_file = create_graph_visualization(graph, output_path)

    return output_file


async def run_decomposition_and_visualize():
    """Run decomposition and create visualization."""
    print("🚀 Running requirement decomposition...")

    agent = RequirementDecomposerAgent()

    hypothesis = Hypothesis(
        original_text="Summarize the mission context for a crewed Mars expedition with emphasis on radiation protection: dominant radiation hazards per phase, and current NASA/ESA/CNSA dose limits.",
        refined_text="",
        context="",
    )

    graph = await agent.execute(hypothesis)

    print(f"\n📊 Graph Statistics:")
    print(f"   Total nodes: {graph.total_nodes}")
    print(f"   Max depth: {graph.max_depth}")
    print(f"   Atomic nodes: {graph.atomic_count}")
    print(f"   Shared nodes: {graph.shared_count}")

    # Save graph for later use
    graph_file = ROOT_DIR / "outputs" / "requirement_graph.json"
    graph.save_to_file(str(graph_file))
    print(f"\n💾 Graph saved to: {graph_file}")

    # Create visualization
    output_file = create_graph_visualization(graph)

    return output_file


if __name__ == "__main__":
    import sys

    # Check if loading from file
    if len(sys.argv) > 1 and sys.argv[1] == "--load":
        # Load from file
        input_file = sys.argv[2] if len(sys.argv) > 2 else str(ROOT_DIR / "outputs" / "requirement_graph.json")
        output_file = sys.argv[3] if len(sys.argv) > 3 else "requirement_graph.html"
        load_and_visualize(input_file, output_file)
    else:
        # Run full decomposition
        asyncio.run(run_decomposition_and_visualize())
