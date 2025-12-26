# Testes de Integração - WhatsApp Webhook

Este diretório contém a infraestrutura para testes de integração manuais do webhook WhatsApp.

## Visão Geral

Os testes de integração **não são automatizados**. Eles funcionam capturando dados reais enviados do seu celular via WhatsApp e armazenando-os localmente para análise manual.

## Como Funciona

Quando o modo `INTEGRATION_TEST_MODE=true` está ativo:

1. O servidor recebe mensagens reais via webhook
2. Extrai os dados da mensagem (texto ou áudio)
3. Se for áudio, faz o download do arquivo
4. Salva tudo em `tests/integration/results/{timestamp}/`
5. Você pode então verificar manualmente se os dados foram extraídos corretamente

## Estrutura de Resultados

Cada mensagem recebida cria um diretório com timestamp:

```
tests/integration/results/
└── 2025-01-15_14-30-45/
    ├── extracted_data.json    # Dados extraídos do webhook
    ├── metadata.json          # Metadados (timestamp, hash, tamanho)
    └── audio_received.ogg     # Arquivo de áudio (se aplicável)
```

### Exemplo: `extracted_data.json` (Texto)

```json
{
  "tipo": "text",
  "telefone": "5511999999999",
  "mensagem_id": "wamid.HBgLMTY1MDUwNzY1MjAVAgARGBI5QTNDQTVCM0Q0Q2RTY3RTcA",
  "timestamp": "1704067200",
  "conteudo": "Olá, como você está?"
}
```

### Exemplo: `extracted_data.json` (Áudio)

```json
{
  "tipo": "audio",
  "telefone": "5511888888888",
  "mensagem_id": "wamid.HBgLMTY1MDUwNzY1MjAVAgARGBI5QTNDQTVCM0Q0Q2RTY3RTcA",
  "timestamp": "1704067300",
  "media_id": "1234567890123456",
  "mime_type": "audio/ogg; codecs=opus"
}
```

### Exemplo: `metadata.json`

```json
{
  "timestamp_recebimento": "2025-01-15T14:30:45.123456",
  "tipo_mensagem": "audio",
  "telefone": "5511888888888",
  "tamanho_bytes": 12345,
  "sha256": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2",
  "mime_type": "audio/ogg; codecs=opus"
}
```

## Guia de Uso

### 1. Preparar Ambiente

```bash
# Copiar .env.example para .env
cp .env.example .env

# Editar .env e definir:
INTEGRATION_TEST_MODE=true
WHATSAPP_TOKEN=seu_token_real
WHATSAPP_PHONE_NUMBER_ID=seu_phone_id_real
WHATSAPP_VERIFY_TOKEN=seu_verify_token_real
```

### 2. Iniciar Servidor

```bash
# Usando uvicorn diretamente
python -m uvicorn app.main:app --reload

# Ou usando o script principal
python main.py
```

### 3. Enviar Mensagens do Celular

1. Abra WhatsApp no seu celular
2. Envie uma mensagem de **texto** para o número WhatsApp configurado
3. Envie uma mensagem de **áudio** para o número WhatsApp configurado
4. Aguarde alguns segundos para processamento

### 4. Verificar Resultados

```bash
# Listar resultados capturados
ls -la tests/integration/results/

# Examinar dados extraídos
cat tests/integration/results/2025-01-15_14-30-45/extracted_data.json
cat tests/integration/results/2025-01-15_14-30-45/metadata.json

# Reproduzir áudio recebido (requer ffplay ou similar)
ffplay tests/integration/results/2025-01-15_14-30-45/audio_received.ogg
```

### 5. Validar Manualmente

- ✅ Abra os arquivos JSON em um editor de texto
- ✅ Verifique se os dados correspondem ao que você enviou
- ✅ Reproduza o áudio para validar qualidade
- ✅ Verifique timestamps e hashes
- ✅ Confirme que o telefone está correto
- ✅ Confirme que o tipo de mensagem está correto

### 6. Limpar Resultados Antigos

```bash
# Remover todos os resultados
rm -rf tests/integration/results/

# Ou usar função helper (se disponível)
python -c "from tests.utils.integration_helpers import clear_integration_results; clear_integration_results()"
```

## Logs

Quando o modo de integração está ativo, você verá logs como:

```
INFO: Mensagem recebida - Tipo: text, Telefone: 5511999999999, ID: wamid.xxx
INFO: Resultado de integração salvo em tests/integration/results/2025-01-15_14-30-45/
```

## Troubleshooting

### Nenhum resultado é salvo

- Verifique se `INTEGRATION_TEST_MODE=true` no `.env`
- Verifique se o servidor está rodando
- Verifique os logs do servidor para erros

### Áudio não é baixado

- Verifique se o `WHATSAPP_TOKEN` está correto
- Verifique se o `WHATSAPP_PHONE_NUMBER_ID` está correto
- Verifique os logs para erros de autenticação

### Erro de permissão ao criar diretórios

- Verifique se você tem permissão de escrita no diretório do projeto
- Execute o servidor com permissões adequadas

## Notas Importantes

- ⚠️ **Não commitar** os resultados de integração no Git (já está no `.gitignore`)
- ⚠️ **Não compartilhar** os arquivos JSON pois contêm números de telefone reais
- ⚠️ **Desativar** o modo de integração em produção (`INTEGRATION_TEST_MODE=false`)
- ⚠️ **Limpar** resultados antigos periodicamente para economizar espaço

## Próximos Passos

Após validar manualmente que os dados estão sendo extraídos corretamente:

1. Desative o modo de integração (`INTEGRATION_TEST_MODE=false`)
2. Implemente a lógica de processamento real (STT, LLM, TTS)
3. Teste o fluxo completo end-to-end
