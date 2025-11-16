import sys
import colorama
from rdflib import Graph
from logger import Logger

from interfaces import count_interfaces, list_interfaces, show_interface_details
from status import status_up, status_down
from inconsistencies import find_inconsistencies, enable_interface, disable_interface

IETF_INTERFACES_FILE = "rdf/ietf-interfaces.ttl"
IETF_IP_FILE = "rdf/ietf-ip.ttl"


def print_menu(instances_file=None, graph_size=0, interfaces_count=0):
    print(f"\n{colorama.Fore.CYAN}==================================== RDF Operations ===================================={colorama.Fore.RESET}")
    print(f"\n{colorama.Fore.YELLOW}[i] Loaded IETF Interfaces File:{colorama.Fore.RESET} {IETF_INTERFACES_FILE}")
    print(f"{colorama.Fore.YELLOW}[i] Loaded IETF IP File:{colorama.Fore.RESET} {IETF_IP_FILE}")
    print(f"{colorama.Fore.YELLOW}[i] Loaded RDF Instances File:{colorama.Fore.RESET} {instances_file if instances_file else 'N/A'}")
    print(f"{colorama.Fore.YELLOW}[i] Total RDF Triples in Graph:{colorama.Fore.RESET} {graph_size}")
    print(f"{colorama.Fore.YELLOW}[i] Total Interfaces Count:{colorama.Fore.RESET} {interfaces_count}")
    
    print(f"\n{colorama.Fore.CYAN}Available operations:{colorama.Fore.RESET}\n")
    print(f"{colorama.Style.BRIGHT}{colorama.Fore.GREEN}  status-up{colorama.Style.NORMAL} <interface_name>{colorama.Fore.RESET} - Set interface status to 'up'")
    print(f"{colorama.Style.BRIGHT}{colorama.Fore.GREEN}  status-down{colorama.Style.NORMAL} <interface_name>{colorama.Fore.RESET} - Set interface status to 'down'")
    print(f"{colorama.Style.BRIGHT}{colorama.Fore.GREEN}  enable{colorama.Style.NORMAL} <interface_name>{colorama.Fore.RESET} - Enable the specified interface")
    print(f"{colorama.Style.BRIGHT}{colorama.Fore.GREEN}  disable{colorama.Style.NORMAL} <interface_name>{colorama.Fore.RESET} - Disable the specified interface")
    print(f"{colorama.Style.BRIGHT}{colorama.Fore.GREEN}  show{colorama.Style.NORMAL} <interface_name>{colorama.Fore.RESET} - Show details of the specified interface")
    print(f"{colorama.Style.BRIGHT}{colorama.Fore.GREEN}  list{colorama.Style.RESET_ALL} - List all interfaces with their details")
    print(f"{colorama.Style.BRIGHT}{colorama.Fore.GREEN}  check-inconsistencies{colorama.Style.RESET_ALL} - Finds all enabled interfaces without an IP address assigned")
    print(f"{colorama.Style.BRIGHT}{colorama.Fore.GREEN}  exit{colorama.Style.RESET_ALL} - Exit the program")
    print(f"\n{colorama.Fore.CYAN}======================================================================================={colorama.Fore.RESET}") 


def main_loop(graph):
    while True:
        command = input(f"\n{colorama.Fore.BLUE}>{colorama.Fore.RESET} ").strip()
        if command == "exit":
            Logger.log("Exiting the program.")
            break
        elif command.startswith("show"):
            _, interface_name = command.split(maxsplit=1)
            details = show_interface_details(graph, interface_name)
            if details:
                print(f"{colorama.Fore.MAGENTA}Interface Details:{colorama.Fore.RESET}")
                for key, value in details.items():
                    print(f"  {key}: {value}")
            else:
                print(f"{colorama.Fore.RED}Interface '{interface_name}' not found.{colorama.Fore.RESET}")
        elif command == "list":
            interfaces = list_interfaces(graph)
            for intf in interfaces:
                print(f"Interface: {intf['name']}, Status: {intf['status']}, Enabled: {intf['enabled']}")
        elif command.startswith("status-up"):
            _, interface_name = command.split(maxsplit=1)
            status_up(graph, interface_name)
            print(f"{colorama.Fore.MAGENTA}Interface '{interface_name}' status set to 'up'.{colorama.Fore.RESET}")
        elif command.startswith("status-down"):
            _, interface_name = command.split(maxsplit=1)
            status_down(graph, interface_name)
            print(f"{colorama.Fore.MAGENTA}Interface '{interface_name}' status set to 'down'.{colorama.Fore.RESET}")
        elif command.startswith("enable"):
            _, interface_name = command.split(maxsplit=1)
            enable_interface(graph, interface_name)
            print(f"{colorama.Fore.MAGENTA}Interface '{interface_name}' enabled.{colorama.Fore.RESET}")
        elif command.startswith("disable"):
            _, interface_name = command.split(maxsplit=1)
            disable_interface(graph, interface_name)
            print(f"{colorama.Fore.MAGENTA}Interface '{interface_name}' disabled.{colorama.Fore.RESET}")
        elif command == "check-inconsistencies":
            inconsistencies = find_inconsistencies(graph)
            if inconsistencies:
                print(f"{colorama.Fore.RED}Inconsistent Interfaces (enabled but no IP address):{colorama.Fore.RESET}")
                for iface, name in inconsistencies:
                    print(f"  Interface: {name} ({iface})")
            else:
                print(f"{colorama.Fore.GREEN}No inconsistencies found.{colorama.Fore.RESET}")
        else:
            Logger.error(f"Unknown command: {command}")


if __name__ == "__main__":
    colorama.init(autoreset=True)

    if len(sys.argv) != 2:
        Logger.error("Usage: python executor.py <instances_file.ttl>")
        sys.exit(1)

    instances_file = sys.argv[1]

    g = Graph()
    
    try:
        g.parse(IETF_INTERFACES_FILE, format='turtle')
        g.parse(IETF_IP_FILE, format='turtle')
    except Exception as e:
        Logger.error(f"Failed to load IETF RDF files: {e}")
        sys.exit(1)

    try:
        g.parse(instances_file, format='turtle')
    except Exception as e:
        Logger.error(f"Failed to load RDF file '{instances_file}': {e}")
        sys.exit(1)

    Logger.log(f"RDF file '{instances_file}' loaded with {len(g)} triples.")

    instances_count = count_interfaces(g)

    print_menu(instances_file, len(g), instances_count)
    main_loop(g)