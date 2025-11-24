# YANG2RDF

## INF01015 – Gerência e Aplicações em Redes

### Trabalho Prático

Na primeira etapa do trabalho, realizamos a tradução de bases de dados de rede usando modelos tradicionais de gerenciamento (YANG) para uma estrutura de grafo do conhecimento (RDF).

* Para este trabalho, utilizamos modelos existentes de YANG para interfaces (`ietf-interfaces`) e IP (`ietf-ip`).
* RDF é usado para armazenar essas informações em um grafo de conhecimento, permitindo representar relações complexas entre interfaces, endereços IP e dispositivos de forma flexível.

Na segunda etapa, implementamos mecanismos de inferência, permitindo executar atividades de gerenciamento sobre o grafo:

* Identificação de interfaces inconsistentes
* Atualização de estados operacionais de interfaces
* Detecção de subnets duplicadas ou sobrepostas

# Uso

### Converter módulos YANG para RDF

```
python converter/yang2rdf.py <yang_file.yang> <output_file.rdf>
```

### Gerar instâncias

Em `instances`, temos um script que gera instâncias para os esquemas `ietf-interfaces` e `ietf-ip`.

```
python instances/generate.py <output_instances_file.rdf>
```

### Executar operações SPARQL

```
python operations/executor.py <instances_file.rdf>
```

```
Available operations:
  status-up <interface_name> - Set interface status to 'up'
  status-down <interface_name> - Set interface status to 'down'
  enable <interface_name> - Enable the specified interface
  disable <interface_name> - Disable the specified interface
  show <interface_name> - Show details of the specified interface
  list - List all interfaces with their details
  check-inconsistencies - Finds all enabled interfaces without an IP address assigned
  verify-overlaps - Finds all overlapping and duplicate CIDR prefixes among interfaces
  exit - Exit the program
```

# Sobre o projeto

## Sub-nets duplicadas ou com overlaps

É indesejado ter endereços de subnet duplicados ou com overlap em uma rede, pois isso pode levar a diversos erros levando a falha de comunição entre as interfaces.

Esses erros geralmente surgem quando um operador humano altera a configuração de um dispositivo sem perceber conflitos com endereços já existentes.

Utilizando do grafo de conhecimento, podemos verificar todas as subnets configuradas para uma rede e checar se há overlaps ou duplicação entre os endereços. 

> Esse problema não poderia ser resolvido apenas com YANG, porque YANG descreve apenas a configuração de cada dispositivo de forma isolada. Ele por si só não inclui as informações de como os diferentes dispositivo de uma rede se relacionam. Um grafo de conhecimento permite navegar por todas as relações, realizar consultas e inferências, o que é essencial para detectar conflitos de endereços em toda a rede.

## Operações SPARQL implementadas

- [x] Gerenciamento de Configuração. Atualizar status de uma interface.
    - Mudar `oper-status` de `down` para `up`.
    - Comandos `status-up <interface>` e `status-down <interface>`.
- [x] Gerenciamento de Falhas. Verificar inconsistência de status.
    - `check-inconsistencies`: 
        - Encontrar interfaces marcadas como `up`, mas sem endereço IP atribuído.
    - `verify-overlaps`:
        - Encontra todas as interfaces com endereços CIDRs duplicados ou com overlap entre as sub-redes.

## Possíveis extensões

A implementação pode ser expandida para outros casos de uso, como:

* Identificação de links vulneráveis na rede
* Análise de topologia e confiabilidade dos dispositivos

Para isso, seria necessário definir uma representação formal dos dispositivos e suas conexões (links) no grafo de conhecimento. Semelhantes aos modelos existentes de YANG que utilizamos para as interfaces (`ietf-interfaces`), poderiamos criar nosso próprio modelo para representar dispositivos, como (`if:Device`) e incluir esta relação em nosso grafo de conhecimento.
