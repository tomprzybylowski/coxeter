from flask import Flask, request, jsonify, send_file, send_from_directory
import networkx as nx
from pyvis.network import Network
import os
import ig

app = Flask(__name__, static_folder='static', static_url_path='/static')

@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")  # serve your HTML from the current folder

@app.route("/sequences")
def get_sequences():
    graph_type = request.args.get("type")
    players = int(request.args.get("players", 1))

    results = []

    with open("sequences_with_info.txt") as f:
        for line in f:
            try:
                parts = line.strip().split(";")
                if len(parts) != 5:
                    continue

                line_type, line_players, line_seq, line_nb_nodes, line_nb_edges = parts

                if line_type == graph_type and int(line_players) == players:
                    results.append({
                        "sequence": eval(line_seq),
                        "num_nodes": int(line_nb_nodes),
                        "num_edges": int(line_nb_edges)
                    })

            except Exception as e:
                print(f"Error parsing line: {line} - {e}")

    return jsonify(results)

@app.route("/graph")
def generate_graph():
    graph_type = request.args.get("type", "complete")
    seq = request.args.get("seq", "default")

    try:
        if graph_type != "B":
            int_sequence = [int(x.strip()) for x in seq.split(",")]
        else:
            int_sequence = [float(x.strip()) for x in seq.split(",")]
    except ValueError:
        return "Invalid sequence format", 400

    # Use your custom graph generator
    ig.draw_interchange_graph(int_sequence, graph_type)

    return "", 204


if __name__ == "__main__":
    # Load the sequences from the file into a dictionary
    app.run(debug=True)
