# Mistral - Transcrição de Áudios - Versão: 1.0.0

## Visão Geral
Este documento explica como usar a API do Mistral para **transcrever áudios**. A API fornece endpoints para transcrever arquivos de áudio em texto, com suporte para múltiplas opções de configuração.

## Pré-requisitos
- Conhecimento básico de APIs REST
- Uma chave de API válida da Mistral
- Arquivo de áudio em um dos formatos suportados

## Endpoints de Transcrição de Áudio

### POST /v1/audio/transcriptions
Endpoint principal para criar uma transcrição de áudio.

## Parâmetros da Requisição

### Request Body

#### file
**Tipo:** File (obrigatório) 
**Descrição:** O objeto File (não o nome do arquivo) a ser enviado. Para fazer upload de um arquivo e especificar um nome customizado, formate sua requisição como:
```
file=@path/to/your/file.mp3;filename=custom_name.mp3
```
Caso contrário, você pode manter o nome original do arquivo:
```
file=@path/to/your/file.mp3
```

#### model
**Tipo:** string (obrigatório)  
**Descrição:** ID do modelo a ser utilizado para a transcrição.

#### language
**Tipo:** string | null (opcional)  
**Descrição:** Idioma do áudio, ex: 'pt' para português ou 'fr' para francês. Fornecer o idioma pode aumentar a precisão da transcrição.

#### temperature
**Tipo:** number | null (opcional)  
**Descrição:** Controla a aleatoriedade da transcrição. Valores menores resultam em transcrições mais determinísticas.

#### diarize
**Tipo:** boolean (padrão: false)  
**Descrição:** Ativa a identificação de falantes múltiplos na transcrição.

#### context_bias
**Tipo:** array<string>  
**Descrição:** Lista de palavras ou frases para viesar a transcrição. Útil para termos específicos do domínio.

#### timestamp_granularities
**Tipo:** array<"segment"|"word">  
**Descrição:** Granularidades de timestamps a incluir na resposta. Pode ser "segment" para segmentos ou "word" para palavras.

#### file_id
**Tipo:** string|null  
**Descrição:** ID de um arquivo previamente enviado para `/v1/files`.

#### file_url
**Tipo:** string|null  
**Descrição:** URL de um arquivo a ser transcrito.

#### stream
**Tipo:** boolean (padrão: false)  
**Descrição:** Se true, a resposta será transmitida como eventos (SSE - Server-Sent Events).

## Exemplos de Implementação

### Python
```python

from mistralai import Mistral
import os

with Mistral(
    api_key=os.getenv("MISTRAL_API_KEY", ""),
) as mistral:

    res = mistral.audio.transcriptions.complete(
        model="voxtral-mini-2507",
        file="path/to/audio/file.mp3"
    )

    # Handle response
    print(res)
```


## Resposta Bem-sucedida (200)

A resposta bem-sucedida retorna um objeto JSON com os seguintes campos:

#### text
**Tipo:** string (obrigatório)  
**Descrição:** O texto transcrito completo do áudio.

#### language
**Tipo:** string|null (obrigatório)  
**Descrição:** O idioma detectado do áudio.

#### model
**Tipo:** string (obrigatório)  
**Descrição:** O modelo utilizado para a transcrição.

#### segments
**Tipo:** array<TranscriptionSegmentChunk>  
**Descrição:** Array de segmentos da transcrição, contendo timestamps e textos individuais.

#### usage
**Tipo:** UsageInfo (obrigatório)  
**Descrição:** Informações sobre o uso da API, incluindo:
- `prompt_audio_seconds`: Duração do áudio em segundos
- `prompt_tokens`: Tokens utilizados para processar o áudio
- `total_tokens`: Total de tokens utilizados
- `completion_tokens`: Tokens utilizados para gerar a transcrição

## Exemplo de Resposta

```json
{
  "model": "voxtral-mini-2507",
  "text": "This week, I traveled to Chicago to deliver my final farewell address to the nation, following in the tradition of presidents before me. It was an opportunity to say thank you...",
  "language": "en",
  "segments": [],
  "usage": {
    "prompt_audio_seconds": 203,
    "prompt_tokens": 4,
    "total_tokens": 3264,
    "completion_tokens": 635
  }
}
```

## Referência da Documentação Oficial
- URL: https://docs.mistral.ai/api/endpoint/audio/transcriptions#operation-audio_api_v1_transcriptions_post
- Versão da API: 1.0.0
