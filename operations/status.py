from rdflib import Literal, URIRef
from rdflib.namespace import RDF

def status_up(graph, interface_name):    
    query = """
    DELETE WHERE {
        inst:%s if:oper-status "down" .
    } ;
    INSERT DATA {
        inst:%s if:oper-status "up" .
    }
    """ % (interface_name, interface_name)

    graph.update(query)


def status_down(graph, interface_name):    
    query = """
    DELETE WHERE {
        inst:%s if:oper-status "up" .
    } ;
    INSERT DATA {
        inst:%s if:oper-status "down" .
    }
    """ % (interface_name, interface_name)

    graph.update(query)