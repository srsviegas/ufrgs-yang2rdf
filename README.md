# YANG2RDF

## Uso

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

## Operações SPARQL planejadas

- [ ] **Gerenciamento de Configuração.** Atualizar status de uma interface.
    - Mudar `oper-status` de `down` para `up`.
    - Comandos `status-up <interface>` e `status-down <interface>`.
- [ ] **Gerenciamento de Falhas.** Verificar inconsistência de status.
    - Encontrar interfaces marcadas como `up`, mas sem endereço IP atribuído.
    - Comando `check-inconsistencies`.
- Outras...