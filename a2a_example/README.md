# A2A Example - Comunicação entre Agentes

Demonstra o protocolo **Agent-to-Agent (A2A)** do ADK: um agente orquestrador
(`a2a_orchestrator`) que delega tarefas para três agentes remotos especializados,
cada um rodando como um servidor próprio:

| Agente            | Porta | Função                          |
| ----------------- | ----- | ------------------------------- |
| `research_agent`  | 8001  | Pesquisa e checagem de fatos    |
| `analysis_agent`  | 8002  | Análise de dados e insights     |
| `content_agent`   | 8003  | Criação de conteúdo e resumos   |

## Pré-requisitos

Tenha o projeto configurado conforme o [README principal](../README.md):
`uv` instalado, `uv sync --all-groups` executado e o `.env` preenchido na raiz.

## Como rodar (Windows e macOS)

Você vai precisar de **dois terminais**, ambos abertos na **raiz** do projeto.

### Terminal 1 - subir os agentes remotos

```bash
uv run python a2a_example/run_servers.py
```

Esse script multiplataforma sobe os três servidores (portas 8001, 8002 e 8003),
espera cada um ficar pronto e mostra o status. Deixe este terminal aberto.

### Terminal 2 - subir o orquestrador

```bash
uv run adk web a2a_example
```

Abra <http://localhost:8000> e selecione **`a2a_orchestrator`** no menu.

### Encerrar

No Terminal 1, pressione **Ctrl+C**. O script encerra os três servidores
automaticamente (não é preciso matar processos na mão).

## Exemplos de prompts

- `"Pesquise as tendências de IA em 2024 e escreva um resumo"`
- `"Analise o mercado de computação quântica e crie um texto sobre isso"`

O orquestrador vai delegar a pesquisa, a análise e a escrita para os agentes
remotos correspondentes.

## Sobre os scripts `.sh`

Os arquivos `start_a2a_servers.sh` e `stop_a2a_servers.sh` continuam disponíveis
como atalho **apenas para macOS/Linux**. No Windows (e como caminho recomendado
em qualquer sistema), use `run_servers.py`, que funciona igual em todos eles.
