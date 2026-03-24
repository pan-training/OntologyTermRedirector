from flask import Flask, request, redirect
from rdflib import Graph, URIRef, Literal, RDFS
from rdflib.paths import ZeroOrMore
from urllib.parse import urlencode

app = Flask(__name__)

terms = Graph()
with open("data/PaNET.owl") as f:
    terms.parse(f, format="xml")
terms.add((URIRef("http://edamontology.org/topic_4012"), RDFS.label, Literal("FAIR data")))


def get_url(term_iri: str, base_url: str, endpoint="materials") -> str:
    """Get the URL to redirect to for a given term IRI."""
    term_labels = list(terms.objects(URIRef(term_iri), ~RDFS.subClassOf * ZeroOrMore / RDFS.label))

    if not term_labels:
        raise ValueError(f"Term not found: {term_iri}")

    return f"{base_url}/{endpoint}?{urlencode([('scientific_topics[]', label) for label in term_labels])}"


@app.route("/")
def root_url():
    """Show something when accessing the server."""
    return {"status": "OK", "description": "Redirect to training materials for given ontology term. Use /ontology-term-search?iri=<term_iri> endpoint."}

@app.route("/ontology-term-search")
def redirect_to_training():
    """Redirect to training materials for given ontology term."""
    term_uri = request.args.get("iri")
    pan_training_url = request.args.get("base_url", request.url_root).rstrip("/")

    if not term_uri:
        return {"error": "No term URI provided. Use /ontology-term-search?iri=<term_iri>."}, 400

    try:
        redirect_url = get_url(term_uri, pan_training_url)
        return redirect(redirect_url)
    except ValueError as e:
        return {"error": str(e), "term_iri": term_uri}, 404
