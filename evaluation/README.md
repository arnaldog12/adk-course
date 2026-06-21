# Evaluation - Avaliação e testes de agentes

Agente único de **atendimento ao cliente** usado como base para demonstrar
padrões de teste e avaliação no Google ADK: testes unitários das ferramentas,
validação da configuração do agente, integração e avaliação automatizada de
**trajetória** e **qualidade da resposta**.

## Funcionalidades do agente

- **Busca em base de conhecimento**: responde perguntas frequentes (reset de
  senha, reembolso, frete, conta, billing e suporte técnico)
- **Criação de tickets** com prioridade (`low`, `normal`, `high`, `urgent`)
  e tempo de resposta estimado
- **Listagem de tickets da sessão** com filtros opcionais por status e
  prioridade
- **Atualização de tickets** (status, prioridade ou descrição)
- **Consulta de status** de um ticket existente pelo ID
- **Persistência por usuário**: tickets ficam guardados em
  `state["user:tickets"]` e sobrevivem entre turnos da mesma sessão

## Conceitos abordados do ADK

- **`output_key`** - a resposta final do agente é gravada em
  `state["support_response"]`
- **Estado da sessão** com prefixo `user:` para persistir tickets entre
  turnos
- **`AgentEvaluator`** - executa avaliações declarativas a partir de
  arquivos JSON
- **Arquivos `.test.json`** - casos de teste de turno único ou
  multi-step com a sequência esperada de ferramentas
- **Arquivos `.evalset.json`** - conjuntos de avaliação multi-turno
- **`test_config.json`** - define os critérios de avaliação
  (`tool_trajectory_avg_score`, `response_match_score`)
- **Testes Pytest** combinados com testes async do `AgentEvaluator`

## Descrição das ferramentas

| Ferramenta             | Argumentos                                              | O que faz |
| ---------------------- | ------------------------------------------------------- | --------- |
| `search_knowledge_base` | `query: str`                                           | Busca artigos relevantes em uma base interna fixa |
| `create_ticket`        | `issue: str`, `priority: str = "normal"`                | Cria um ticket com ID `TICK-XXXXXXXX` e estimativa de resposta |
| `list_tickets`         | `status?: str`, `priority?: str`                        | Lista os tickets da sessão, com filtros opcionais |
| `update_ticket`        | `ticket_id: str`, `status?`, `priority?`, `issue?`      | Atualiza um ou mais campos de um ticket existente |
| `check_ticket_status`  | `ticket_id: str`                                        | Retorna a situação atual de um ticket pelo ID |

Valores válidos:

- `priority`: `low`, `normal`, `high`, `urgent`
- `status`: `open`, `in_progress`, `resolved`, `closed`

## Exemplos de prompts

- `"Como faço para resetar minha senha?"`
- `"Minha conta foi completamente bloqueada!"` (gera ticket urgente)
- `"Qual é a política de reembolso?"`
- `"Crie um ticket de prioridade alta sobre erro 500 ao fazer checkout"`
- `"Liste todos os meus tickets abertos"`
- `"Mude o ticket TICK-ABC123 para resolved"`
- `"Verifique o status do ticket TICK-ABC123"`

## Testes e avaliação

Rode toda a suíte a partir da **raiz** do projeto:

```bash
uv run pytest
```

A suíte cobre:

- Testes unitários das ferramentas (`TestToolFunctions`)
- Validação da configuração do agente (`TestAgentConfiguration`)
- Fluxos de integração (`TestIntegration`)
- Avaliação de trajetória e resposta (`TestAgentEvaluation`,
  via `AgentEvaluator`)

Arquivos de avaliação:

- `tests/simple.test.json` - busca simples na base de conhecimento
- `tests/ticket_creation.test.json` - fluxo de criação de ticket
- `tests/complex.evalset.json` - conversa de múltiplos turnos
- `tests/test_config.json` - critérios de avaliação

Métricas:

- **Trajectory score** (0,0-1,0) - precisão da sequência de ferramentas
  chamadas pelo agente
- **Response score** (0,0-1,0) - similaridade da resposta final com a
  esperada (0,9+ excelente, 0,7-0,8 bom)

Comandos úteis:

```bash
uv run pytest -v -s     # testes com saída detalhada
uv run ruff check       # verifica estilo de código
```

### Rodando via CLI (`adk eval`)

Você também pode executar uma avaliação direto pela CLI, sem passar por
Pytest. A partir da **raiz** do projeto:

```bash
uv run adk eval \
  --config_file_path evaluation/tests/test_config.json \
  --print_detailed_results \
  evaluation \
  evaluation/tests/simple.test.json
```

Assinatura do comando:

```
adk eval [OPTIONS] AGENT_MODULE_FILE_PATH [EVAL_SET_FILE_PATH_OR_ID]...
```

- `AGENT_MODULE_FILE_PATH`: caminho para a **pasta** que contém o
  `__init__.py` com `root_agent` (aqui, `evaluation`). Não aponte para
  `evaluation/agent.py` -- o ADK espera o diretório do módulo.
- `EVAL_SET_FILE_PATH_OR_ID`: um ou mais arquivos `.test.json` /
  `.evalset.json` (ex.: `evaluation/tests/simple.test.json`).
- `--config_file_path`: aponta para o `test_config.json` (critérios como
  `tool_trajectory_avg_score` e `response_match_score`). É opcional;
  sem ele, o ADK usa os critérios padrão. **Não confunda com o eval set.**
- `--print_detailed_results`: imprime a tabela detalhada por invocação.

Os resultados ficam salvos em `evaluation/.adk/eval_history/`.

## Como rodar

A partir da **raiz** do projeto (veja o [README principal](../README.md)
para o setup inicial):

```bash
uv sync --all-groups   # uma vez
uv run adk web         # abre http://localhost:8000
```

Abra <http://localhost:8000> e selecione **evaluation** no menu.
Confirme que o `.env` da raiz está preenchido com sua `GOOGLE_API_KEY`.

## Próximos passos

Sugestões de extensão para praticar:

- **Criar um novo `.evalset.json`** com uma conversa multi-turno que
  combina várias ferramentas (ex.: criar um ticket, listar e depois
  atualizar o ticket criado), e rodar com o `AgentEvaluator`.
- **Ajustar os critérios de avaliação** em `tests/test_config.json`
  (`tool_trajectory_avg_score`, `response_match_score`) e observar como
  o resultado dos testes muda.
- **Adicionar uma nova ferramenta** ao agente (ex.: `delete_ticket`) e
  cobrir com testes unitários, de integração e um `.test.json` de
  avaliação.
- **Expandir a base de conhecimento** em `tools.py` para tópicos novos
  (ex.: política de troca, garantia) e criar um `.test.json` que valida
  a resposta correta.
- **Plugar uma base real**: trocar o dicionário `KNOWLEDGE_BASE` por uma
  busca em embedding/vector store e ajustar os testes para mockar a
  chamada externa.
