def find_inconsistencies(graph):
    query = """
    SELECT ?iface ?name
    WHERE {
        ?iface a if:Interface ;
            if:name ?name ;
            if:enabled true .

        FILTER NOT EXISTS {
            ?ipv4 a ip:ipv4-address ;
                ip:interface ?iface .
        }

        FILTER NOT EXISTS {
            ?ipv6 a ip:ipv6-address ;
                ip:interface ?iface .
        }
    }
    """

    results = graph.query(query)

    return [(row.iface, row.name) for row in results]


def enable_interface(graph, interface_name):
    query = """
    DELETE WHERE {
        inst:%s if:enabled false .
    } ;
    INSERT DATA {
        inst:%s if:enabled true .
    }
    """ % (interface_name, interface_name)

    graph.update(query)


def disable_interface(graph, interface_name):
    query = """
    DELETE WHERE {
        inst:%s if:enabled true .
    } ;
    INSERT DATA {
        inst:%s if:enabled false .
    }
    """ % (interface_name, interface_name)

    graph.update(query)