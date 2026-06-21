# Curso ADK - Agentes com Google ADK

Exemplos práticos do curso de criação de agentes com o **Google Agent Development Kit (ADK)**.
Este repositório foi preparado para rodar **igual no Windows e no macOS**, sem nuvem.

Você só precisa instalar **uma** ferramenta: o `uv`. Ele cuida do resto (baixa o Python 3.12
e instala todas as dependências). Todos os comandos do curso são `uv run ...` e funcionam
exatamente da mesma forma nos dois sistemas.

## Sumário

- [Pré-requisito: instalar o uv](#pré-requisito-instalar-o-uv)
- [Opção A - Setup nativo (recomendado)](#opção-a---setup-nativo-recomendado)
- [Opção B - Dev Container (Docker)](#opção-b---dev-container-docker)
- [Configurar a chave de API (.env)](#configurar-a-chave-de-api-env)
- [Como rodar cada módulo](#como-rodar-cada-módulo)
- [Testes e lint](#testes-e-lint)
- [Solução de problemas](#solução-de-problemas)

## Pré-requisito: instalar o uv

O [`uv`](https://docs.astral.sh/uv/) é um gerenciador de projetos Python. Instale uma vez:

**Windows (PowerShell):**

```powershell
winget install --id=astral-sh.uv -e
```

Se não tiver `winget`, use:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS:**

```bash
brew install uv
```

Ou, sem Homebrew:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Depois de instalar, **feche e reabra o terminal** e confirme:

```bash
uv --version
```

> Você **não** precisa instalar Python à parte. O `uv` lê o arquivo [.python-version](.python-version)
> e baixa o Python 3.12 automaticamente.

## Opção A - Setup nativo (recomendado)

Esta é a forma mais leve e indicada para a maioria dos alunos.

1. Clone o repositório e entre na pasta:

   ```bash
   git clone <url-do-repositorio>
   cd adk-course
   ```

2. Instale tudo (o `uv` baixa o Python e as dependências):

   ```bash
   uv sync --all-groups
   ```

3. Configure sua chave de API (veja [Configurar a chave de API](#configurar-a-chave-de-api-env)).

4. Suba a interface web do ADK:

   ```bash
   uv run adk web
   ```

   Abra <http://localhost:8000> e escolha o módulo no menu (ex.: `content_moderator`).

## Opção B - Dev Container (Docker)

Use esta opção se quiser um ambiente **idêntico** ao de todos os outros alunos, isolado do
seu sistema. Roda localmente (ainda sem nuvem), mas exige Docker.

1. Instale o [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows ou macOS).
2. Instale o [Visual Studio Code](https://code.visualstudio.com/) e a extensão
   **Dev Containers** (`ms-vscode-remote.remote-containers`).
3. Abra a pasta do projeto no VS Code.
4. Quando aparecer o aviso, clique em **"Reopen in Container"**
   (ou use a paleta de comandos: `Dev Containers: Reopen in Container`).
5. O container instala tudo sozinho (`uv sync`). Quando terminar, use os mesmos comandos:

   ```bash
   uv run adk web
   ```

   A porta 8000 é encaminhada automaticamente; abra <http://localhost:8000>.

> Não esqueça de configurar o `.env` (veja abaixo) antes de rodar os agentes.

## Configurar a chave de API (.env)

Os agentes usam a API do Google Gemini. Crie o arquivo `.env` a partir do exemplo:

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**

```bash
cp .env.example .env
```

Depois abra o arquivo `.env` e preencha sua chave:

```dotenv
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=coloque_sua_chave_aqui
```

Gere uma chave gratuita no [Google AI Studio](https://aistudio.google.com/apikey).

> O `.env` fica na **raiz** do projeto e é carregado automaticamente quando você roda os
> comandos a partir da raiz. Ele está no `.gitignore`, então sua chave nunca é enviada ao Git.

## Como rodar cada módulo

Rode todos os comandos a partir da **raiz** do projeto. A maneira mais simples é abrir a
interface web e escolher o módulo no menu suspenso:

```bash
uv run adk web
```

Módulos disponíveis no menu:

| Módulo                      | Tema                                                  |
| --------------------------- | ----------------------------------------------------- |
| `content_moderator`         | Callbacks e guardrails (moderação de conteúdo)        |
| `mcp_integration`           | Integração com MCP (operações de arquivo com aprovação) |
| `multi_agent_orchestration` | Orquestração de múltiplos agentes (paralelo/sequencial) |
| `evaluation`                | Avaliação e testes de agentes                         |

> O módulo `mcp_integration` precisa de um pré-requisito extra (Node.js). Veja
> [mcp_integration/README.md](mcp_integration/README.md).

O módulo **a2a_example** (comunicação entre agentes) tem um fluxo próprio com vários
servidores. Veja [a2a_example/README.md](a2a_example/README.md).

## Solução de problemas

- **`uv: command not found` / não reconhecido**: feche e reabra o terminal após instalar o
  `uv`. No Windows, reabra o PowerShell.
- **Erro de chave de API**: confirme que o arquivo `.env` existe na raiz e que
  `GOOGLE_API_KEY` está preenchido (sem aspas).
- **Porta 8000 em uso**: rode em outra porta, por exemplo `uv run adk web --port 8080`.
- **Primeira execução lenta**: na primeira vez o `uv` baixa o Python e as dependências; as
  próximas execuções são rápidas.

> *Made with ❤️ for the ADK Community*

> Heavily inspired in this [amazing training][source].

[source]: https://github.com/raphaelmansuy/adk_training
