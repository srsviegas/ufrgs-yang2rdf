import sys
from rdflib import Graph
from logger import Logger

IETF_INTERFACES_FILE = "rdf/ietf-interfaces.ttl"
IETF_IP_FILE = "rdf/ietf-ip.ttl"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        Logger.error("Usage: python executor.py <instances_file.ttl>")
        sys.exit(1)

    instances_file = sys.argv[1]

    g = Graph()
    g.parse(IETF_INTERFACES_FILE, format='turtle')
    g.parse(IETF_IP_FILE, format='turtle')
    g.parse(instances_file, format='turtle')

    Logger.log(f"RDF file '{instances_file}' loaded with {len(g)} triples.")

    q = """
    SELECT ?node ?label
    WHERE {
    ?node a yang:Leaf ;
            rdfs:label ?label .
    }
    LIMIT 5
    """

    for row in g.query(q):
        print(row)