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
    structural_keywords = {
        "module", "submodule", "container", "list", "leaf", "leaf-list",
        "choice", "case", "grouping", "augment", "uses", "rpc",
        "input", "output", "typedef", "identity", "notification"
    }

    literal_keywords = {
        "type", "default", "units", "description", "config", "mandatory",
        "range", "length", "pattern", "value", "status", "when",
        "if-feature", "must", "reference", "min-elements", "max-elements",
        "fraction-digits", "bit", "position"
    }

    for child in statement.substmts:
        kw = child.keyword
        arg = child.arg

        if not kw:
            continue

        if kw in structural_keywords:
            if arg:
                frag = make_uri_fragment(arg)
            else:
                frag = f"{kw}_{id(child)}"

            node_uri = URIRef(namespace[frag])
            graph.add((node_uri, RDF.type, namespace[kw.capitalize()]))
            if arg:
                graph.add((node_uri, RDFS.label, Literal(arg)))
            graph.add((parent_uri, namespace.hasChild, node_uri))

            process_statement(graph, child, node_uri)

        elif kw in literal_keywords:
            if arg is not None:
                graph.add((parent_uri, namespace[kw.capitalize()], Literal(arg)))
            for grand in child.substmts:
                if grand.keyword in structural_keywords:
                    process_statement(graph, grand, parent_uri)
                else:
                    if grand.arg is not None:
                        graph.add((parent_uri, namespace[grand.keyword.capitalize()], Literal(grand.arg)))

        elif kw == "enum":
            if arg:
                frag = f"enum_{make_uri_fragment(arg)}"
            else:
                frag = f"enum_{id(child)}"
            node_uri = URIRef(namespace[frag])
            graph.add((node_uri, RDF.type, namespace.Enum))
            graph.add((node_uri, RDFS.label, Literal(arg if arg else "")))
            graph.add((parent_uri, namespace.hasChild, node_uri))
            process_statement(graph, child, node_uri)

        else:
            if arg is not None:
                graph.add((parent_uri, namespace[kw.capitalize()], Literal(arg)))
            for grand in child.substmts:
                if grand.arg is not None:
                    graph.add((parent_uri, namespace[grand.keyword.capitalize()], Literal(grand.arg)))


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