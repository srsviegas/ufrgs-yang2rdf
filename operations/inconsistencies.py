import colorama

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


def get_all_ipv4_networks(graph):
    query = """
    PREFIX ip: <urn:ietf:params:xml:ns:yang:ietf-ip#>
    PREFIX if: <urn:ietf:params:xml:ns:yang:ietf-interfaces#>

    SELECT ?ipv4Inst ?iface ?cidr ?start ?end
    WHERE {
        ?ipv4Inst a ip:ipv4-address ;
                  ip:interface ?iface .

        OPTIONAL { ?ipv4Inst ip:cidr ?cidr . }
        OPTIONAL { ?ipv4Inst ip:network-start ?start . }
        OPTIONAL { ?ipv4Inst ip:network-end ?end . }
    }
    """
    result = graph.query(query)

    networks = []
    for row in result:
        iface_name = str(row.iface).split("#")[-1]
        networks.append({
            "interface": iface_name,
            "cidr": str(row.cidr) if row.cidr else None,
            "start": int(row.start) if row.start else None,
            "end": int(row.end) if row.end else None,
        })
    return networks

def find_duplicate_prefixes(networks):
    seen = {}
    duplicates = []

    # checks for exact duplicates using start and end
    # so it assumes that these values are correct
    # for the respective CIDRs associated to it
    for net in networks:
        key = (net["start"], net["end"])

        if key in seen:
            duplicates.append((seen[key], net))
        else:
            seen[key] = net

    return duplicates

def find_overlapping_prefixes(networks):
    # checks for overlaps using the comparison between the integer
    # values from the start and end of each network
    overlaps = []

    for i in range(len(networks)):
        for j in range(i+1, len(networks)):
            A = networks[i]
            B = networks[j]

            if A["start"] is None or B["start"] is None:
                continue

            if A["start"] <= B["end"] and B["start"] <= A["end"]:
                if not (A["start"] == B["start"] and A["end"] == B["end"]):
                    overlaps.append((A, B))
    
    return overlaps


def verify_overlaps(g):
    networks = get_all_ipv4_networks(g)

    dups = find_duplicate_prefixes(networks)
    overlaps = find_overlapping_prefixes(networks)

    print("Duplicate prefixes:")
    for a, b in dups:
        print(f"\t{colorama.Fore.RED}{a['interface']} <--> {b['interface']} ({a['cidr']})")
    if not dups:
        print(f"\t{colorama.Fore.GREEN}  No duplicates  found.")

    print("Overlapping prefixes:")
    for a, b in overlaps:
        print(f"\t{colorama.Fore.RED}{a['interface']} ({a['cidr']}) overlaps {b['interface']} ({b['cidr']})")
    if not overlaps:
        print(f"\t{colorama.Fore.GREEN}  No overlaps found.")