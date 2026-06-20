# MCP Integration - Operações de arquivo com aprovação (Human-in-the-Loop)

Demonstra a integração do ADK com o **Model Context Protocol (MCP)**. O agente se conecta a
um servidor MCP de sistema de arquivos e oferece operações de arquivo (criar, mover, apagar)
com um fluxo de **aprovação humana** para operações destrutivas.

Por segurança, o agente fica restrito à pasta `sample_files/`.

## Pré-requisito adicional: Node.js

Além do `uv` (veja o [README principal](../README.md)), este módulo precisa do **Node.js**,
porque o servidor MCP é iniciado via `npx`. Funciona igual no Windows e no macOS.

**Windows (PowerShell):**

```powershell
winget install --id=OpenJS.NodeJS.LTS -e
```

**macOS:**

```bash
brew install node
```

Feche e reabra o terminal e confirme:

```bash
node --version
npx --version
```

> Na primeira execução, o `npx` baixa o pacote `@modelcontextprotocol/server-filesystem`
> automaticamente (precisa de internet nesse primeiro uso).

## Como rodar

A partir da **raiz** do projeto:

```bash
uv sync --all-groups   # uma vez
uv run adk web         # abre http://localhost:8000
```

Abra <http://localhost:8000> e selecione **mcp_integration** no menu.
Confirme que o `.env` da raiz está preenchido com sua `GOOGLE_API_KEY`.

## Exemplo de interação

```text
user: cria um arquivo markdown com o texto "olá"
assistant:
A operação write_file para criar o arquivo meuarquivo.md com o conteúdo "olá" requer sua aprovação.
Para prosseguir, digite 'approve' para habilitar a aprovação automática para todas as operações
de arquivo, ou 'deny' para cancelar esta operação.

user: aprovado
assistant: arquivo criado com sucesso

user: cria uma pasta chamada minha_pasta
assistant: pasta criada com sucesso

user: desabilite a aprovação automática
assistant: A aprovação automática para operações de arquivo foi desabilitada.

user: cria uma nova pasta chamada pasta_2
assistant: A operação create_directory para criar a pasta pasta_2 requer sua aprovação.
```
