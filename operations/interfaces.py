def count_interfaces(graph):
    query = """
    SELECT (COUNT(?interface) AS ?interfaces)
    WHERE {
        ?interface a if:Interface .
    }
    """

    result = graph.query(query)

    for row in result:
        return row.interfaces
    
def show_interface_details(graph, interface_name):
    query = """
    SELECT ?interface ?name ?enabled ?operStatus ?ipv4 ?prefix ?ipv6
    WHERE {
        ?interface a if:Interface ;
            if:name ?name ;
            if:enabled ?enabled ;
            if:oper-status ?operStatus .

        OPTIONAL {
            ?ipv4Inst a ip:ipv4-address ;
                    ip:interface ?interface ;
                    ip:ip ?ipv4 ;
                    ip:prefix-length ?prefix .
        }

        OPTIONAL {
            ?ipv6Inst a ip:ipv6-address ;
                    ip:interface ?interface ;
                    ip:ip ?ipv6 .
        }

        FILTER (?name = "%s")
    }
    """ % interface_name

    result = graph.query(query)

    for row in result:
        return {
            'interface': str(row.interface),
            'name': str(row.name),
            'enabled': str(row.enabled),
            'oper-status': str(row.operStatus),
            'ipv4': str(row.ipv4) if row.ipv4 else None,
            'prefix-length': str(row.prefix) if row.prefix else None,
            'ipv6': str(row.ipv6) if row.ipv6 else None
        }

def list_interfaces(graph):
    query = """
    SELECT ?interface ?name ?status ?enabled
    WHERE {
        ?interface a if:Interface ;
            if:enabled ?enabled ;
            if:name ?name ;
            if:oper-status ?status .
    }
    """

    result = graph.query(query)

    interfaces = []
    for row in result:
        interfaces.append({
            'interface': str(row.interface),
            'name': str(row.name),
            'status': str(row.status),
            'enabled': str(row.enabled)
        })
    return interfaces