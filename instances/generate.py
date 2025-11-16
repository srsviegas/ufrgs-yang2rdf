import sys
from rdflib import Graph, Namespace, Literal, RDF, URIRef

# Namespaces
INST = Namespace("http://example.org/instances#")
IF = Namespace("urn:ietf:params:xml:ns:yang:ietf-interfaces#")
IP = Namespace("urn:ietf:params:xml:ns:yang:ietf-ip#")

def generate_instances():
    g = Graph()

    g.bind("inst", INST)
    g.bind("if", IF)
    g.bind("ip", IP)

    # Fake interfaces to generate
    interfaces = [
        {
            "name": "eth0",
            "enabled": True,
            "oper_status": "up",
            "ipv4": "192.168.10.1",
            "prefix": 24,
            "ipv6": "fe80::1"
        },
        {
            "name": "eth1",
            "enabled": True,
            "oper_status": "down",  # inconsistency
            "ipv4": "10.0.0.5",
            "prefix": 24
        },
        {
            "name": "eth2",
            "enabled": True,
            "oper_status": "up",
            # No IP (another inconsistency)
        }
    ]

    for iface in interfaces:
        iface_uri = INST[iface["name"]]

        # Instance type: Interface
        g.add((iface_uri, RDF.type, IF.Interface))

        # Leaves
        g.add((iface_uri, IF.name, Literal(iface["name"])))
        g.add((iface_uri, IF.enabled, Literal(iface["enabled"])))
        g.add((iface_uri, IF["oper-status"], Literal(iface["oper_status"])))

        # IPv4
        if "ipv4" in iface:
            ipv4_uri = INST[f"{iface['name']}_ipv4"]
            g.add((ipv4_uri, RDF.type, IP["ipv4-address"]))
            g.add((ipv4_uri, IP.ip, Literal(iface["ipv4"])))
            g.add((ipv4_uri, IP["prefix-length"], Literal(iface["prefix"])))
            g.add((ipv4_uri, IP.interface, iface_uri))

        # IPv6
        if "ipv6" in iface:
            ipv6_uri = INST[f"{iface['name']}_ipv6"]
            g.add((ipv6_uri, RDF.type, IP["ipv6-address"]))
            g.add((ipv6_uri, IP.ip, Literal(iface["ipv6"])))
            g.add((ipv6_uri, IP.interface, iface_uri))

    return g


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate.py <instances_output_file.ttl>")
        sys.exit(1)

    output_file = sys.argv[1]

    g = generate_instances()

    g.serialize(output_file, format="turtle")
    print(f"Generated {output_file}")