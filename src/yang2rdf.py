import sys
import re
import time

from rdflib import Graph, Literal, RDF, RDFS, URIRef, Namespace
from pyang import repository, context

from logger import Logger


namespace = Namespace("http://example.org/yang#")


def make_uri_fragment(name):
    sanitized = re.sub(r'[^a-zA-Z0-9_\-]', '_', name)
    return sanitized


def process_statement(graph, statement, parent_uri):
    for child in statement.substmts:
        node_uri = URIRef(namespace[make_uri_fragment(child.arg)])
        graph.add((node_uri, RDF.type, namespace[child.keyword.capitalize()]))
        graph.add((node_uri, RDFS.label, Literal(child.arg)))
        graph.add((parent_uri, namespace.hasChild, node_uri))
        process_statement(graph, child, node_uri)


def yang_to_rdf(yang_file, rdf_file):
    rep = repository.FileRepository()
    ctx = context.Context(rep)

    with open(yang_file, 'r') as f:
        yang_data = f.read()
    module = ctx.add_module('module', yang_data, in_format='yang')
    ctx.validate()

    Logger.log(f"Parsed YANG module: {module.arg}")

    g = Graph()
    g.bind("yang", namespace)

    module_uri = URIRef(namespace[make_uri_fragment(module.arg)])
    g.add((module_uri, RDF.type, namespace.Module))
    g.add((module_uri, RDFS.label, Literal(module.arg)))

    process_statement(graph=g, statement=module, parent_uri=module_uri)

    g.serialize(destination=rdf_file, format='turtle')

    Logger.log(f"RDF data written to {rdf_file}.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        Logger.error("Usage: python yang2rdf.py <input_yang_file> <output_rdf_file>")
        sys.exit(1)


    input_file = sys.argv[1]
    output_file = sys.argv[2]

    Logger.log(f"Converting {input_file} to {output_file}...")

    yang_to_rdf(input_file, output_file)