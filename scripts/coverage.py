"""Helper script to determine what ontology terms are covered by training materials."""

import sys

from rdflib import Graph, RDF, RDFS, OWL, URIRef
import requests

from ontology_term_redirector.main import get_url


def get_paNET_terms(g):
    return {
        term
        for term in g.subjects(RDF.type, OWL.Class)
        if "PaNET" in str(term)
    }


def get_subclasses(g, term, panet_terms):
    """Return all PaNET subclasses of term, recursively."""
    result = set()

    for subclass in g.subjects(RDFS.subClassOf, term):
        if subclass in panet_terms:
            result.add(subclass)
            result.update(get_subclasses(g, subclass, panet_terms))

    return result


def get_baseclasses(g, term, panet_terms):
    """Return all PaNET base classes/ancestors of term, recursively."""
    result = set()

    for baseclass in g.objects(term, RDFS.subClassOf):
        if baseclass in panet_terms:
            result.add(baseclass)
            result.update(get_baseclasses(g, baseclass, panet_terms))

    return result


def expand_coverage(g, covered, panet_terms, include_subclasses, include_baseclasses):
    """Expand directly covered terms according to the command-line options."""
    expanded = set(covered)

    if include_subclasses:
        for term in panet_terms:
            if get_subclasses(g, term, panet_terms) & covered:
                expanded.add(term)

    if include_baseclasses:
        for term in panet_terms:
            if get_baseclasses(g, term, panet_terms) & covered:
                expanded.add(term)

    return expanded


def main():
    include_subclasses = "--subclasses" in sys.argv
    include_baseclasses = "--baseclasses" in sys.argv

    g = Graph()
    with open("data/PaNET.owl") as f:
        g.parse(f, format="xml")

    panet_terms = get_paNET_terms(g)

    covered = []
    not_covered = []
    errored = []

    all_terms = sorted(panet_terms, key=str)

    for i, term in enumerate(all_terms):
        url = get_url(
            str(term),
            "https://pan-training.eu",
            endpoint="materials.json",
        )
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

        print(
            f"{symbol} Checked term {i+1}/{len(all_terms)}: "
            f"{term} ({g.value(term, RDFS.label)})"
        )

    # Keep the API results as the source of "directly covered" terms,
    # then expand them according to the selected options.
    directly_covered = set(covered)

    covered = expand_coverage(
        g,
        directly_covered,
        panet_terms,
        include_subclasses,
        include_baseclasses,
    )

    not_covered = set(all_terms) - covered - set(errored)

    display_hierarchy(g, covered, not_covered, errored)

    print(f"Covered: {len(covered)}")
    print(f"Not covered: {len(not_covered)}")
    print(f"Errored: {len(errored)}")
    print(f"Covered Percentage: {len(covered) / len(all_terms) * 100:.2f}%")

    print()
    print("Options:")
    print("  --subclasses   Also consider a term covered when one of its subclasses is covered.")
    print("  --baseclasses  Also consider a term covered when one of its base classes is covered.")
    print("  Both options can be used together.")


def display_hierarchy(
    g,
    covered,
    not_covered,
    errored,
    term=URIRef("http://purl.org/pan-science/PaNET/PaNET00001"),
    level=0,
):
    label = g.value(term, RDFS.label) or term

    if term in covered:
        symbol = "✅"
    elif term in not_covered:
        symbol = "❌"
    else:
        symbol = "⚠️"

    print("  " * level + f"{symbol} {label} ({term})")

    if term not in not_covered:
        subclasses = sorted(
            g.subjects(RDFS.subClassOf, term),
            key=lambda x: str(g.value(x, RDFS.label)),
        )

        for subclass in subclasses:
            if "PaNET" in str(subclass):
                display_hierarchy(
                    g,
                    covered,
                    not_covered,
                    errored,
                    term=subclass,
                    level=level + 1,
                )
            else:
                print(
                    "  " * (level + 1)
                    + f"⚠️ {g.value(subclass, RDFS.label) or subclass} "
                    f"({subclass}) - Not a PaNET term"
                )


if __name__ == "__main__":
    main()
