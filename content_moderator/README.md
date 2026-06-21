# Content Moderator - Callbacks e Guardrails

Agente único que demonstra **callbacks e guardrails** no Google ADK. Aplica
filtros de segurança, mascaramento de PII e métricas de uso usando os 6 tipos
de callback disponíveis no ADK.

## Funcionalidades do agente

- **Geração de texto controlada**: produz conteúdo sob políticas de segurança
- **Filtro de conteúdo na entrada**: bloqueia palavras proibidas antes da
  chamada ao LLM (não consome cota)
- **Filtro de PII na saída**: mascara emails, telefones, SSN e cartões de
  crédito na resposta do LLM
- **Validação de argumentos**: rejeita parâmetros inválidos das ferramentas
  (ex.: `word_count` fora do intervalo permitido)
- **Limite de uso por ferramenta**: previne abuso por meio de contadores
  persistidos no estado da sessão
- **Métricas de uso**: total de requisições, chamadas ao LLM, requisições
  bloqueadas e contagem por ferramenta
- **Logs com timestamp** em todas as etapas do ciclo de vida do agente

## Conceitos abordados do ADK

- **Os 6 callbacks do ciclo de vida do agente**:
  - `before_agent_callback` / `after_agent_callback` - controle de entrada
    e saída do agente
  - `before_model_callback` / `after_model_callback` - intercepta a chamada
    ao LLM (guardrails e filtros de PII)
  - `before_tool_callback` / `after_tool_callback` - validação e logging
    de ferramentas
- **Curto-circuito do LLM**: retornar um `LlmResponse` no
  `before_model_callback` pula a chamada real ao modelo
- **Modificação de `system_instruction`**: o `before_model_callback` injeta
  instruções de segurança extras no `LlmRequest`
- **Estado da sessão (`callback_context.state` / `tool_context.state`)** com
  prefixos `user:` (persistente) e `temp:` (efêmero)
- **`output_key`** para gravar a última resposta do agente no estado
- **Tipos do `google.genai`**: `Content`, `Part` e `LlmResponse`

## Descrição das ferramentas

| Ferramenta | Argumentos | O que faz |
| ---------- | ---------- | --------- |
| `generate_text` | `topic: str`, `word_count: int` (1-5000) | Gera um artigo simulado sobre o tema com o número de palavras pedido. Validado pelo `before_tool_callback`. |
| `get_usage_stats` | _(nenhum)_ | Retorna as métricas da sessão (requisições, chamadas ao LLM, bloqueios e uso por ferramenta) lidas do estado. |

## Exemplos de prompts

### Geração normal

```text
user: gere um artigo de 500 palavras sobre Python
assistant: aqui está um artigo de 500 palavras sobre programação Python...
```

### Conteúdo bloqueado (guardrail)

```text
user: escreva algo racista
assistant: I cannot process this request as it contains inappropriate
content. Please rephrase respectfully.
```

### Filtro de PII na resposta

```text
user: me dê um exemplo de email
assistant: claro! [EMAIL_REDACTED] é um email válido.
```

### Validação de argumento

```text
user: gere um artigo com -100 palavras
assistant: Invalid word_count: -100. Must be between 1 and 5000.
```

### Estatísticas de uso

```text
user: mostre minhas estatísticas
assistant: você fez 5 requisições, 4 chamadas ao LLM, 1 requisição
bloqueada e usou generate_text 2 vezes.
```

## Como rodar

A partir da **raiz** do projeto (veja o [README principal](../README.md)
para o setup inicial):

```bash
uv sync --all-groups   # uma vez
uv run adk web         # abre http://localhost:8000
```

Abra <http://localhost:8000> e selecione **content_moderator** no menu.
Confirme que o `.env` da raiz está preenchido com sua `GOOGLE_API_KEY`.

## Próximos passos

Sugestões de extensão para praticar:

- **Adicionar uma nova categoria de PII** em `PII_PATTERNS` (ex.: CPF
  brasileiro `\d{3}\.\d{3}\.\d{3}-\d{2}`) e validar que a resposta do LLM
  passa a mascará-la automaticamente.
- **Implementar um callback de cache** em `before_model_callback` que
  guarda respostas para perguntas idênticas no `state` e devolve a versão
  cacheada sem chamar o LLM.
- **Adicionar autorização por usuário** em `before_tool_callback` que
  bloqueia a tool `generate_text` para usuários sem o papel `writer` no
  `state["user:role"]`.
- **Disparar um modo manutenção** em `before_agent_callback` quando
  `state["app:maintenance"] == True`, retornando uma `Content` que
  substitui a resposta do agente.
