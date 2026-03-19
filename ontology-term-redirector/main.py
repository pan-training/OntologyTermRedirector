from flask import Flask, request, redirect
from rdflib import Graph, URIRef, Literal, RDFS

PAN_TRAINING_URL = "https://pan-training.eu"

app = Flask(__name__)


terms = Graph()
terms.add((URIRef("http://edamontology.org/topic_4012"), RDFS.label, Literal("FAIR data")))


@app.route("/")
def root_url():
    """Show something when accessing the server."""
    return {"status": "OK", "description": "Redirect to training materials for given ontology term. Use /term/<term_id> endpoint."}

@app.route("/term")
def redirect_to_training():
    """Redirect to training materials for given ontology term."""
    term_uri = request.args.get("uri")

    if not term_uri:
        return {"error": "No term URI provided. Use /term?uri=<term_uri>."}, 400

    term_labels = list(terms.objects(URIRef(term_uri), RDFS.label))

    if not term_labels:
        return {"error": "Term not found", "term_uri": term_uri}, 404

    return redirect(f"{PAN_TRAINING_URL}/materials?scientific_topics={term_labels[0]}")