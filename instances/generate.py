import sys
import random
from rdflib import Graph, Namespace, Literal, RDF, URIRef

INST = Namespace("http://example.org/instances#")
IF   = Namespace("urn:ietf:params:xml:ns:yang:ietf-interfaces#")
IP   = Namespace("urn:ietf:params:xml:ns:yang:ietf-ip#")

DEFAULT_COUNT = 20
INCONSISTENCY_PCT = 0.15 


def random_ip_v4():
    net = random.choice([
        (10, 0, 0, 0),
        (172, random.randint(16, 31), 0, 0),
        (192, 168, random.randint(0, 255), 0)
    ])
    return f"{net[0]}.{net[1]}.{net[2]}.{random.randint(1, 254)}"


def random_ip_v6():
    return f"fe80::{random.randint(0, 0xffff):04x}:{random.randint(0, 0xffff):04x}"


def random_prefix():
    return random.choice([24, 25, 26, 27, 28, 29, 30])


def random_oper_status():
    return random.choice(["up", "down"])


def generate_instances(count: int = DEFAULT_COUNT, inconsistency_pct: float = INCONSISTENCY_PCT) -> Graph:
    g = Graph()
    g.bind("inst", INST)
    g.bind("if",   IF)
    g.bind("ip",   IP)

    for i in range(count):
        name = f"eth{i}"
        enabled = random.choice([True, False])
        oper_status = random_oper_status()

        iface_uri = INST[name]

        g.add((iface_uri, RDF.type, IF.Interface))
        g.add((iface_uri, IF.name, Literal(name)))
        g.add((iface_uri, IF.enabled, Literal(enabled)))
        g.add((iface_uri, IF["oper-status"], Literal(oper_status)))

        has_ip = True
        if enabled and random.random() < inconsistency_pct:
            has_ip = False

        if has_ip:
            ipv4_addr = random_ip_v4()
            prefix = random_prefix()
            ipv4_uri = INST[f"{name}_ipv4"]
            g.add((ipv4_uri, RDF.type, IP["ipv4-address"]))
            g.add((ipv4_uri, IP.ip, Literal(ipv4_addr)))
            g.add((ipv4_uri, IP["prefix-length"], Literal(prefix)))
            g.add((ipv4_uri, IP.interface, iface_uri))

            if random.random() < 0.5:
                ipv6_addr = random_ip_v6()
                ipv6_uri = INST[f"{name}_ipv6"]
                g.add((ipv6_uri, RDF.type, IP["ipv6-address"]))
                g.add((ipv6_uri, IP.ip, Literal(ipv6_addr)))
                g.add((ipv6_uri, IP.interface, iface_uri))


    return g


def usage():
    print("Usage: python generate_random_instances.py <output.ttl> [count] [incons%]", file=sys.stderr)
    print("  count      – number of interfaces (default 20)", file=sys.stderr)
    print("  incons%    – inconsistency percentage (0‑100, default 15)", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()

    output_file = sys.argv[1]

    count = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_COUNT
    incons = float(sys.argv[3]) / 100.0 if len(sys.argv) > 3 else INCONSISTENCY_PCT

    if count <= 0 or not (0 <= incons <= 1):
        usage()

    g = generate_instances(count=count, inconsistency_pct=incons)
    g.serialize(destination=output_file, format="turtle")
    print(f"Generated {count} interfaces → {output_file}")
    print(f"  • {incons*100:.0f}% enabled but without IP (inconsistencies)")