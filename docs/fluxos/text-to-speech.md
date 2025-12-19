# Fluxo de Integração da API Murf.ai - Text-to-Speech

## Visão Geral
Este documento descreve o fluxo completo para converter texto em áudio usando a API Murf.ai, desde a preparação do texto até a recuperação do arquivo de áudio sintetizado.

## Etapas do Fluxo

### 1. Preparação e Autenticação

#### Obtenção da Chave de API
- Acessar o [Painel de API Murf](https://murf.ai/api/dashboard)
- Gerar uma chave de API única
- Armazenar a chave como variável de ambiente: `MURF_API_KEY`

#### Instalação do SDK Python (Opcional)
Se usar o SDK Python:
```bash
pip install murf
```

---

### 2. Envio da Solicitação de Síntese

#### Endpoint da API
**URL:** `https://api.murf.ai/v1/speech/generate` (Endpoint padrão)

**Método HTTP:** `POST`

#### Headers Obrigatórios
```
Content-Type: application/json
Authorization: Bearer {MURF_API_KEY}
```

#### Corpo da Requisição (JSON)

**Parâmetros Obrigatórios:**
| Parâmetro | Tipo | Descrição | Exemplo |
|-----------|------|-----------|---------|
| `text` | string | Texto a ser convertido em fala (máximo 5000 caracteres) | "Bonjour, comment allez-vous?" |
| `voice_id` | string | ID da voz a ser usada | "fr-FR-adélie" |

**Parâmetros Opcionais:**
| Parâmetro | Tipo | Valor Padrão | Descrição |
|-----------|------|--------------|-----------|
| `style` | string | "Conversational" | Estilo de fala: Calm, Conversational, Promo, Sad, Angry |
| `format` | string | "WAV" | Formato do áudio: MP3, WAV, FLAC, ALAW, ULAW, PCM, OGG |
| `channel_type` | string | "MONO" | Tipo de canal: MONO, STEREO |
| `sample_rate` | integer | 22050 | Taxa de amostragem: 8000, 16000, 22050, 44100, 48000 |
| `rate` | integer | 0 | Velocidade da fala: -50 a 50 |
| `pitch` | integer | 0 | Tom da voz: -50 a 50 |
| `variation` | integer | 1 | Variação na prosódia: 0-5 (Gen2 model) |
| `encode_as_base_64` | boolean | false | Retornar áudio codificado em Base64 em vez de URL |

#### Exemplos de Requisição

**Exemplo 1: Usando SDK Python**
```python
from murf import Murf

client = Murf(
    api_key="SUA_CHAVE_API"  # Ou variável de ambiente MURF_API_KEY
)

res = client.text_to_speech.generate(
    text="Bonjour, comment allez-vous aujourd'hui?",
    voice_id="fr-FR-adélie",
    style="Calm",
    format="OGG",
    channel_type="STEREO",
    sample_rate=44100
)
```

**Exemplo 2: Usando cURL**
```bash
curl -X POST https://api.murf.ai/v1/speech/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "text": "Bonjour, comment allez-vous aujourd'\''hui?",
    "voice_id": "fr-FR-adélie",
    "style": "Calm",
    "format": "OGG",
    "channel_type": "STEREO",
    "sample_rate": 44100
  }'
```

**Exemplo 3: Usando Python Requests**
```python
import requests
import json

url = "https://api.murf.ai/v1/speech/generate"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_API_KEY"
}

payload = {
    "text": "Bonjour, comment allez-vous aujourd'hui?",
    "voice_id": "fr-FR-adélie",
    "style": "Calm",
    "format": "OGG",
    "channel_type": "STEREO",
    "sample_rate": 44100
}

response = requests.post(url, headers=headers, json=payload)
result = response.json()
```

---

### 3. Processamento da Resposta

#### Resposta de Sucesso (Status 200 OK)

A API retorna um JSON com a seguinte estrutura:

```json
{
  "audioFile": "https://murf-audio-cdn.s3.amazonaws.com/audio-xxxxx.mp3",
  "audioLengthInSeconds": 2.5,
  "remainingCharacterCount": 9999,
  "consumedCharacterCount": 48,
  "encodedAudio": null,
  "wordDurations": [
    {
      "word": "Bonjour",
      "startMs": 0,
      "endMs": 500,
      "sourceWordIndex": 0,
      "pitchScaleMinimum": 0.9,
      "pitchScaleMaximum": 1.1
    }
  ],
  "warning": null
}
```

#### Campos da Resposta

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `audioFile` | string | URL do arquivo de áudio gerado (válido por 72 horas) |
| `audioLengthInSeconds` | double | Duração do áudio em segundos |
| `remainingCharacterCount` | long | Número de caracteres restante no ciclo de faturação atual |
| `consumedCharacterCount` | integer | Número de caracteres processados nesta requisição |
| `encodedAudio` | string \| null | Áudio em Base64 (se `encode_as_base_64=true`), senão null |
| `wordDurations` | array | Informações de timing para cada palavra |
| `warning` | string \| null | Mensagens de aviso (se houver) |

---

### 4. Recuperação do Arquivo de Áudio

#### Opção A: Download via URL (Padrão)

```python
import requests

# A partir da resposta anterior
audio_url = result["audioFile"]

# Baixar o arquivo
audio_response = requests.get(audio_url)

# Salvar o arquivo
with open("output.mp3", "wb") as f:
    f.write(audio_response.content)
```

**Características:**
- URL válida por 72 horas
- Formato: URL HTTP/HTTPS
- Recomendado para arquivos grandes
- Reduz latência de transferência

#### Opção B: Base64 Encoding (Inline)

```python
import base64

# Usar encode_as_base_64=true na requisição anterior
encoded_audio = result["encodedAudio"]

# Decodificar e salvar
audio_bytes = base64.b64decode(encoded_audio)

with open("output.mp3", "wb") as f:
    f.write(audio_bytes)
```

**Características:**
- Áudio retornado diretamente na resposta
- Não requer download adicional
- Útil para aplicações serverless
- Menor latência (sem requisição HTTP adicional)
- Sem limites de tempo (não expira)

---

## Vozes Francesas Disponíveis

### Vozes Femininas

| Voice ID | Nome | Idade | Estilos Disponíveis |
|----------|------|-------|---------------------|
| `fr-FR-adélie` | Adélie | Meia-idade | Calm, Conversational, Promo, Sad |
| `fr-FR-justine` | Justine | Jovem adulta | Angry, Calm, Conversational, Promo, Sad |
| `fr-FR-louise` | Louise | Meia-idade | Conversational |

### Vozes Masculinas

| Voice ID | Nome | Idade | Estilos Disponíveis |
|----------|------|-------|---------------------|
| `fr-FR-maxime` | Maxime | Meia-idade | Conversational |
| `fr-FR-axel` | Axel | Meia-idade | Conversational |
| `fr-FR-guillaume` | Guillaume | Meia-idade | Conversational |
| `fr-FR-louis` | Louis | Jovem adulto | Conversational, Promo |

### Vozes Canadenses

| Voice ID | Nome | Idade | Estilos Disponíveis |
|----------|------|-------|---------------------|
| `fr-CA-clément` | Clément | Jovem adulto | Conversational |
| `fr-CA-alexis` | Alexis | Jovem adulto | Conversational |

---

## Fluxo Completo Simplificado

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. PREPARAÇÃO                                                   │
│    - Obter chave de API (MURF_API_KEY)                         │
│    - Instalar SDK Python (opcional)                            │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│ 2. REQUISIÇÃO POST                                              │
│    - URL: https://api.murf.ai/v1/speech/generate               │
│    - Headers: Authorization: Bearer {MURF_API_KEY}             │
│    - Body: { text, voice_id, style, format, ... }             │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│ 3. PROCESSAMENTO DA API                                         │
│    - Síntese de voz (texto → áudio)                            │
│    - Compressão e codificação                                  │
│    - Geração de URL ou Base64                                  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│ 4. RESPOSTA 200 OK                                              │
│    - audioFile: URL do áudio                                   │
│    - audioLengthInSeconds: duração                             │
│    - encodedAudio: Base64 (se solicitado)                      │
│    - wordDurations: timing das palavras                        │
│    - remainingCharacterCount: créditos restantes               │
└──────────────────────┬──────────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────────────┐  ┌────────▼──────────────────┐
│ OPÇÃO A: Download URL  │  │ OPÇÃO B: Usar Base64     │
│                        │  │                           │
│ GET {audioFile}        │  │ Decodificar encodedAudio │
│ (válido 72 horas)      │  │ (sem limites de tempo)   │
└───────┬────────────────┘  └────────┬──────────────────┘
        │                             │
        └──────────────┬──────────────┘
                       │
                ┌──────▼──────────┐
                │  ARQUIVO ÁUDIO  │
                │   (MP3/WAV)     │
                └─────────────────┘
```

---

## Boas Práticas

### 1. Cache de Áudio
```python
# Armazenar em cache áudios já gerados para evitar requisições repetidas
cache = {}

def get_audio(text, voice_id, style="Conversational"):
    cache_key = f"{text}_{voice_id}_{style}"
    
    if cache_key in cache:
        return cache[cache_key]
    
    # Gerar novo áudio
    response = client.text_to_speech.generate(
        text=text,
        voice_id=voice_id,
        style=style
    )
    
    cache[cache_key] = response
    return response
```

### 2. Tratamento de Erros
```python
try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    result = response.json()
except requests.exceptions.Timeout:
    print("Timeout na requisição")
except requests.exceptions.HTTPError as e:
    print(f"Erro HTTP: {e.response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Erro na requisição: {e}")
```

### 3. Validação de Entrada
```python
def validate_text(text):
    if not text or len(text) > 5000:
        raise ValueError("Texto deve ter entre 1 e 5000 caracteres")
    return text

def validate_voice_id(voice_id, available_voices):
    if voice_id not in available_voices:
        raise ValueError(f"Voz {voice_id} não disponível")
    return voice_id
```

### 4. Escolha de Formato
- **OGG**: Melhor compressão para streaming
- **MP3**: Recomendado para aplicações web (menor tamanho)
- **WAV**: Melhor qualidade para aplicações desktop
- **FLAC**: Alta fidelidade, se o tamanho não for limitação
- **ALAW/ULAW**: Telefonia (mono, 8000 Hz obrigatório)

### 5. Taxa de Amostragem
- **8000 Hz**: Telefonia
- **16000 Hz**: Padrão mínimo para qualidade aceitável
- **44100 Hz**: Qualidade alta (CD)
- **48000 Hz**: Qualidade profissional

---

## Tratamento de Erros Comuns

| Problema | Causa | Solução |
|----------|-------|---------|
| `401 Unauthorized` | Chave API inválida ou ausente | Verificar `MURF_API_KEY` e headers |
| `400 Bad Request` | Parâmetros inválidos | Validar `voice_id`, `format`, `text` |
| `429 Too Many Requests` | Rate limit atingido | Implementar retry com backoff exponencial |
| `Arquivo não encontrado` | URL expirou (>72 horas) | Regenerar áudio ou usar `encode_as_base_64=true` |
| `Formatos ALAW/ULAW em STEREO` | Combinação inválida | Usar MONO e sample_rate 8000 |
| `Texto muito longo` | Excedem 5000 caracteres | Dividir em múltiplas requisições |

---

## Exemplo Completo de Integração

```python
import requests
import base64
import os
from datetime import datetime

class MurfTextToSpeech:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("MURF_API_KEY")
        self.base_url = "https://api.murf.ai/v1/speech/generate"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def synthesize(self, text, voice_id, style="Conversational", 
                   format="MP3", output_path=None):
        """
        Sintetizar texto em áudio
        
        Args:
            text (str): Texto a ser sintetizado (máx 5000 caracteres)
            voice_id (str): ID da voz (ex: "fr-FR-adélie")
            style (str): Estilo de fala
            format (str): Formato do áudio
            output_path (str): Caminho para salvar o arquivo
        
        Returns:
            dict: Resposta da API com URL ou dados do áudio
        """
        
        # Validar entrada
        if not text or len(text) > 5000:
            raise ValueError("Texto deve ter entre 1 e 5000 caracteres")
        
        # Preparar payload
        payload = {
            "text": text,
            "voice_id": voice_id,
            "style": style,
            "format": format,
            "encode_as_base_64": False  # Se True, retorna Base64
        }
        
        # Fazer requisição
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Salvar arquivo se output_path fornecido
        if output_path:
            if result.get("encodedAudio"):
                # Decodificar Base64
                audio_bytes = base64.b64decode(result["encodedAudio"])
                with open(output_path, "wb") as f:
                    f.write(audio_bytes)
            else:
                # Baixar via URL
                audio_response = requests.get(result["audioFile"])
                audio_response.raise_for_status()
                with open(output_path, "wb") as f:
                    f.write(audio_response.content)
        
        return result

# Uso
if __name__ == "__main__":
    tts = MurfTextToSpeech()
    
    result = tts.synthesize(
        text="Bienvenue dans notre application de synthèse vocale.",
        voice_id="fr-FR-adélie",
        style="Conversational",
        format="MP3",
        output_path="output.mp3"
    )
    
    print(f"Áudio gerado: {result['audioFile']}")
    print(f"Duração: {result['audioLengthInSeconds']} segundos")
    print(f"Caracteres restantes: {result['remainingCharacterCount']}")
```

---

## Referências

- [Documentação Oficial - API Murf](https://murf.ai/api/docs)
- [Painel de API Murf](https://murf.ai/api/dashboard)
- [Referência da API - Text-to-Speech](https://murf.ai/api/docs/api-reference/text-to-speech/generate)
