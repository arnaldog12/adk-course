# MCP Integration - Operações de arquivo com aprovação humana

Agente único que integra o Google ADK ao **Model Context Protocol (MCP)**.
Conecta-se a um servidor MCP de sistema de arquivos via `npx` e oferece
operações de arquivo com um fluxo de **aprovação humana (Human-in-the-Loop)**
para operações destrutivas.

Por segurança, o agente fica restrito à pasta `sample_files/`.

## Funcionalidades do agente

- **Operações de leitura sem aprovação**: listar diretórios, ler arquivos,
  buscar por padrão, obter metadados
- **Operações destrutivas com aprovação humana**: criar, escrever, mover ou
  criar diretórios exigem que o usuário responda `approve` (ou outro sinal
  positivo)
- **Modo auto-aprovação**: o usuário pode habilitar/desabilitar a aprovação
  automática para todas as operações destrutivas dentro da sessão
- **Sandbox de diretório**: o servidor MCP é iniciado limitado a
  `sample_files/`, impedindo acesso a arquivos do sistema
- **Logs e contadores de uso** em todas as chamadas de ferramenta

## Conceitos abordados do ADK

- **`MCPToolset`** + **`StdioConnectionParams`** + **`StdioServerParameters`**
  para conectar a um servidor MCP iniciado via `npx`
- **`before_tool_callback` como guardrail** - bloqueia operações destrutivas
  retornando um `dict` no lugar do resultado real da ferramenta
- **Estado da sessão** (`tool_context.state`) com chaves `user:` (persistente
  por usuário) e `temp:` (efêmera, só durante a invocação)
- **`generate_content_config`** com `temperature=0.2` para tornar as
  operações de arquivo mais determinísticas
- **`instruction` parametrizada** - o caminho da pasta sandbox é injetado
  no prompt do agente
- **Mistura de toolsets e ferramentas locais**: o agente combina o
  `McpToolset` com a função local `set_file_ops_approval`

## Descrição das ferramentas

### Vindas do servidor MCP filesystem (sem aprovação)

| Ferramenta | O que faz |
| ---------- | --------- |
| `read_file` / `read_text_file` | Lê o conteúdo de um arquivo |
| `list_directory` | Lista o conteúdo de um diretório |
| `search_files` | Busca arquivos por padrão (glob) |
| `get_file_info` | Retorna metadados (tamanho, datas, tipo) |

### Vindas do servidor MCP filesystem (exigem aprovação)

| Ferramenta | O que faz |
| ---------- | --------- |
| `write_file` / `write_text_file` | Cria ou atualiza arquivos |
| `create_directory` | Cria uma nova pasta |
| `move_file` | Move ou renomeia um arquivo |

### Ferramenta local

| Ferramenta | Argumentos | O que faz |
| ---------- | ---------- | --------- |
| `set_file_ops_approval` | `enabled: bool` | Liga/desliga a auto-aprovação para operações destrutivas. Persiste em `user:auto_approve_file_ops`. |

## Exemplos de prompts

```text
user: cria um arquivo markdown com o texto "olá"
assistant:
A operação write_file para criar o arquivo meuarquivo.md com o conteúdo "olá"
requer sua aprovação. Para prosseguir, digite 'approve' para habilitar a
aprovação automática para todas as operações de arquivo, ou 'deny' para
cancelar esta operação.

user: aprovado
assistant: arquivo criado com sucesso

user: cria uma pasta chamada minha_pasta
assistant: pasta criada com sucesso

user: desabilite a aprovação automática
assistant: A aprovação automática para operações de arquivo foi desabilitada.

user: cria uma nova pasta chamada pasta_2
assistant: A operação create_directory para criar a pasta pasta_2 requer
sua aprovação.
```

## Como rodar

### Pré-requisito adicional: Node.js

Além do `uv` (veja o [README principal](../README.md)), este módulo precisa
do **Node.js**, porque o servidor MCP é iniciado via `npx`. Funciona igual
no Windows e no macOS.

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

> Na primeira execução, o `npx` baixa o pacote
> `@modelcontextprotocol/server-filesystem` automaticamente (precisa de
> internet nesse primeiro uso).

### Subir o agente

A partir da **raiz** do projeto:

```bash
uv sync --all-groups   # uma vez
uv run adk web         # abre http://localhost:8000
```

Abra <http://localhost:8000> e selecione **mcp_integration** no menu.
Confirme que o `.env` da raiz está preenchido com sua `GOOGLE_API_KEY`.

## Próximos passos

Sugestões de extensão para praticar:

- **Trocar o servidor MCP**: substitua `@modelcontextprotocol/server-filesystem`
  por outro servidor da [lista oficial](https://github.com/modelcontextprotocol/servers)
  (ex.: `server-git`, `server-brave-search`) e ajuste a `instruction` do
  agente para refletir as novas capacidades.
- **Adicionar uma nova operação destrutiva**: extenda
  `destructive_operations` com `delete_file` e crie a confirmação
  correspondente no `before_tool_callback`.
- **Aprovação granular por operação**: em vez do flag global
  `auto_approve_file_ops`, guardar aprovações específicas por operação
  (ex.: `user:auto_approve_write_file = True`).
- **Persistir o histórico de operações** num arquivo dentro de
  `sample_files/` via `after_tool_callback`, gerando uma trilha de
  auditoria.
