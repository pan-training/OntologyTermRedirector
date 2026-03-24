"""Helper script to determine what ontology terms are covered by training materials."""

from rdflib import Graph, RDF, RDFS, OWL, URIRef
import requests

from ontology_term_redirector.main import get_url

def main():
    g = Graph()
    with open("data/PaNET.owl") as f:
        g.parse(f, format="xml")

    covered = []
    not_covered = []
    errored = []
    all_terms = [term for term in g.subjects(RDF.type, OWL.Class) if "PaNET" in str(term)]

    for i, term in enumerate(all_terms):
        url = get_url(str(term), "https://pan-training.eu", endpoint="materials.json")
        result = requests.get(url)
        if result.status_code != 200:
            print(f"Error fetching materials for term {term}: {result.status_code}")
            print(result.text)
            print(f"URL was: {url}")
            errored.append(term)
            continue
        if result.json():
            covered.append(term)
            symbol = "✅"
        else:
            not_covered.append(term)
            symbol = "❌"

        print(f"{symbol} Checked term {i+1}/{len(all_terms)}: {term} ({g.value(term, RDFS.label)})")

    display_hierarchy(g, covered, not_covered, errored)

    print(f"Covered: {len(covered)}")
    print(f"Not covered: {len(not_covered)}")
    print(f"Errored: {len(errored)}")
    print(f"Covered Percentage: {len(covered) / len(all_terms) * 100:.2f}%")


def display_hierarchy(g, covered, not_covered, errored, term=URIRef("http://purl.org/pan-science/PaNET/PaNET00001"), level=0):
    label = g.value(term, RDFS.label) or term
    if term in covered:
        symbol = "✅"
    elif term in not_covered:
        symbol = "❌"
    else:
        symbol = "⚠️"
    print("  " * level + f"{symbol} {label} ({term})")

    if term not in not_covered:
        subclasses = sorted(g.subjects(RDFS.subClassOf, term), key=lambda x: str(g.value(x, RDFS.label)))
        for subclass in subclasses:
            if "PaNET" in str(subclass):
                display_hierarchy(g, covered, not_covered, errored, term=subclass, level=level+1)
            else:
                print("  " * (level + 1) + f"⚠️ {g.value(subclass, RDFS.label) or subclass} ({subclass}) - Not a PaNET term")
        

if __name__ == "__main__":
    main()
