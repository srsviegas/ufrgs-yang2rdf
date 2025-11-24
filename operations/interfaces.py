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
    query = f"""
    SELECT ?interface ?name ?enabled ?operStatus ?ipv4 ?prefix ?ipv6 ?cidr ?start ?end
    WHERE {{
        ?interface a if:Interface ;
            if:name ?name ;
            if:enabled ?enabled ;
            if:oper-status ?operStatus .

        OPTIONAL {{
            ?ipv4Inst a ip:ipv4-address ;
                      ip:interface ?interface ;
                      ip:ip ?ipv4 .

            OPTIONAL {{ ?ipv4Inst ip:prefix-length ?prefix . }}
            OPTIONAL {{ ?ipv4Inst ip:cidr ?cidr . }}
            OPTIONAL {{ ?ipv4Inst ip:network-start ?start . }}
            OPTIONAL {{ ?ipv4Inst ip:network-end ?end . }}
        }}

        OPTIONAL {{
            ?ipv6Inst a ip:ipv6-address ;
                      ip:interface ?interface ;
                      ip:ip ?ipv6 .
        }}

        FILTER (?name = "{interface_name}")
    }}
    """

    result = graph.query(query)

    for row in result:
        return {
            'interface': str(row.interface),   # clean URI → "eth9"
            'name': str(row.name),
            'enabled': str(row.enabled),
            'oper-status': str(row.operStatus),
            'ipv4': str(row.ipv4) if row.ipv4 else None,
            'prefix-length': str(row.prefix) if row.prefix else None,
            'cidr': str(row.cidr) if row.cidr else None,
            'network-start': str(row.start) if row.start else None,
            'network-end': str(row.end) if row.end else None,
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