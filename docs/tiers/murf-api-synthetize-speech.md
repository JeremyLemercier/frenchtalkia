# Visão Geral da API Murf - Versão: 1.0.0

## Visão Geral
Este documento cobre as capacidades de Texto para Fala da API Murf AI, destinado a desenvolvedores que desejam integrar síntese de voz em suas aplicações.

## Pré-requisitos
- Conhecimento básico de APIs REST
- Chave de API da Murf (obtida do Painel de API Murf)
- Python 3.7+ (para usar o SDK Python) ou ambiente JavaScript/Node.js

## Início Rápido
A API Murf fornece uma poderosa API de Texto para Fala que permite gerar fala de alta qualidade e som natural a partir de entrada de texto. A API suporta mais de 35 idiomas e 20 estilos de fala em mais de 150 vozes para atender às necessidades da sua aplicação.

### Instalação do SDK
Se estiver usando Python, instale o SDK Python da Murf:
```bash
pip install murf
```

### Usando a API de Texto para Fala
```python
from murf import Murf

client = Murf(
    api_key="SUA_CHAVE_API"  # Não necessário se definiu a variável de ambiente MURF_API_KEY
)

res = client.text_to_speech.generate(
    text="Bienvenu dans notre application",
    voice_id="fr-FR-adélie",

)

print(res.audio_file)
```

Um exemplo de resposta dessa requisição seria:
```json
{
  "audioFile": "string",
  "audioLengthInSeconds": 1.1,
  "remainingCharacterCount": 1,
  "wordDurations": [
    {
      "endMs": 1,
      "startMs": 1,
      "word": "string",
      "pitchScaleMaximum": 1.1,
      "pitchScaleMinimum": 1.1,
      "sourceWordIndex": 1
    }
  ],
  "encodedAudio": "string",
  "warning": "string",
  "consumedCharacterCount": 1
}
```

## Exemplos Detalhados

### Síntese Básica com Voz Francesa
```python
from murf import Murf

client = Murf()
res = client.text_to_speech.generate(
    text="Bonjour, comment allez-vous aujourd'hui?",
    voice_id="fr-FR-adélie",
    style="Calm"
)
```

### Especificando Formato de Saída
```python
from murf import Murf

client = Murf()
res = client.text_to_speech.generate(
    text="Comment puis-je vous aider?",
    voice_id="fr-FR-maxime",
    format="MP3",
    channel_type="MONO",
    sample_rate=44100
)
```
### Usando Diferentes Estilos de Voz
```python
from murf import Murf

client = Murf()

# Estilo Promocional
res_promo = client.text_to_speech.generate(
    text="Découvrez notre nouvelle collection!",
    voice_id="fr-FR-justine",
    style="Promo"
)

# Estilo Conversacional
res_conv = client.text_to_speech.generate(
    text="Comment puis-je vous aider?",
    voice_id="fr-FR-maxime",
    style="Conversational"
)
```

### Codificação Base64
Você pode receber o arquivo de áudio em formato codificado Base64:
```python
from murf import Murf

client = Murf()
res = client.text_to_speech.generate(
    text="Bonjour, comment allez-vous?",
    voice_id="fr-FR-louise",
    encode_as_base_64=True
)
```

A resposta incluirá o arquivo audio codificado em Base64, para ser decodificado e usado em sua aplicação:
```json
{
  ...,
  "encodedAudio": "U29tZSB0ZXh0IHNob3cgd2l0aCB0aGF0Lg==...",
  ...
}
```


### Suporte gzip
Respostas da API Murf podem ser compactadas com gzip:
```python
from murf import Murf

client = Murf()

res = client.text_to_speech.generate(
    text="Bonjour, comment allez-vous aujourd'hui?",
    voice_id="fr-FR-guillaume",
    encode_as_base_64=True,
    request_options={
        'additional_headers': {
            'accept-encoding': 'gzip'
        }
    }
)
```

## Parâmetros da API

### Parâmetros Obrigatórios
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `text` | string | Texto a ser convertido em fala (máximo 5000 caracteres) |
| `voice_id` | string | ID da voz a ser usada (ex: "fr-FR-adélie") |

### Parâmetros Opcionais
| Parâmetro | Tipo | Descrição | Padrão |
|-----------|------|-----------|--------|
| `style` | string | Estilo de fala (Calm, Conversational, Promo, Sad, Angry) | Conversational |
| `format` | string | Formato de áudio (MP3, WAV, FLAC, ALAW, ULAW, PCM, OGG) | WAV |
| `channel_type` | string | Tipo de canal (MONO, STEREO) | MONO |
| `sample_rate` | integer | Taxa de amostragem (8000, 16000, 22050, 44100, 48000) | 22050 |
| `encode_as_base_64` | boolean | Set to true to receive audio in response as a Base64 encoded string instead of a url. This enables zero retention of audio data on Murf's servers | false |
| `rate` | interger | Velocidade da fala (de -50 até 50) | 0 |
| `pitch` | integer | Tom da voz (de -50 até 50) | 0 |
| `variation` | integer | Higher values will add more variation in terms of Pause, Pitch, and Speed to the voice. Only available for Gen2 model (0-5) | 1 |

## Vozes Francesas Disponíveis

### Vozes Femininas
| ID da Voz | Nome | Idade | Estilos Disponíveis |
|-----------|------|-------|---------------------|
| `fr-FR-adélie` | Adélie | Meia-idade | Calm, Conversational, Promo, Sad |
| `fr-FR-justine` | Justine | Jovem adulta | Angry, Calm, Conversational, Promo, Sad |
| `fr-FR-louise` | Louise | Meia-idade | Conversational |

### Vozes Masculinas
| ID da Voz | Nome | Idade | Estilos Disponíveis |
|-----------|------|-------|---------------------|
| `fr-FR-maxime` | Maxime | Meia-idade | Conversational |
| `fr-FR-axel` | Axel | Meia-idade | Conversational |
| `fr-FR-guillaume` | Guillaume | Meia-idade | Conversational |
| `fr-FR-louis` | Louis | Jovem adulto | Conversational, Promo |

### Vozes Canadenses
| ID da Voz | Nome | Idade | Estilos Disponíveis |
|-----------|------|-------|---------------------|
| `fr-CA-clément` | Clément | Jovem adulto | Conversational |
| `fr-CA-alexis` | Alexis | Jovem adulto | Conversational |

## Formatos de Saída Suportados
A API suporta múltiplos formatos de saída para o áudio gerado - o formato padrão é WAV:

| Formato | Descrição | Casos de Uso |
|---------|------------|--------------|
| **WAV** | Áudio não comprimido | Aplicações de baixa latência |
| **MP3** | Áudio comprimido | Redução de tamanho de arquivo |
| **FLAC** | Áudio comprimido sem perdas | Alta fidelidade |
| **ALAW** | Áudio comprimido | Telefonia (mono, 8000 Hz) |
| **ULAW** | Áudio comprimido | Telefonia (mono, 8000 Hz) |

## Resposta da API

### Estrutura da Resposta 200 OK
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `audio_file` | string | Format "url" |
| `audioLengthInSeconds` | double | Tempo do aúdio em segundos |
| `remainingCharacterCount` | long | Número de caráter restante disponível para síntetização no atual ciclo de faturação |
| `encodedAudio` | string or null | Caso encode_as_base_64=False será retornado o URL e o encodedAudio será null |
| `warning` | string or null | Mensagem de aviso, se houver |


### Campos da Resposta
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `audio_file` | string | URL do arquivo de áudio gerado (válido por 72 horas) |
| `encodedAudio` | string | Áudio codificado em Base64 (se solicitado) |
| `character_count` | integer | Número de caracteres processados |
| `duration` | float | Duração do áudio em segundos |
| `voice_id` | string | ID da voz usada |
| `format` | string | Formato do áudio |
| `sample_rate` | integer | Taxa de amostragem |
| `channel_type` | string | Tipo de canal |


## Solução de Problemas
- **Problema**: Formatos ULAW e ALAW suportam apenas canal mono e taxa de amostragem de 8000 Hz → **Solução**: Se especificar tipo de canal ou taxa de amostragem diferente, a API usará os valores suportados automaticamente
- **Problema**: Arquivo de áudio não está disponível → **Solução**: Verifique se o link expirou (arquivos ficam disponíveis por 72 horas após a geração)
- **Problema**: Erro de autenticação → **Solução**: Verifique se sua chave de API está correta e definida como variável de ambiente MURF_API_KEY
- **Problema**: Texto muito longo → **Solução**: O limite é de 5000 caracteres por requisição. Divida textos longos em múltiplas requisições
- **Problema**: Estilo não disponível para a voz selecionada → **Solução**: Verifique a lista de estilos disponíveis para cada voz específica
- **Problema**: Áudio com baixa qualidade → **Solução**: Experimente diferentes taxas de amostragem (44100 para alta qualidade) e formatos (WAV para melhor qualidade)


## Melhores Práticas
1. **Cache de Áudio**: Armazene em cache áudios gerados para evitar requisições repetidas
2. **Tratamento de Erros**: Implemente retry automático para falhas de rede
3. **Validação**: Valide o texto de entrada antes de enviar para a API
4. **Formato**: Use MP3 para aplicações web e WAV para aplicações desktop
5. **Estilo**: Escolha o estilo apropriado para o contexto da aplicação

## Documentos Relacionados
- [Documentação Oficial da API Murf](https://murf.ai/api/docs)
- [Referência da API de Texto para Fala overview](https://murf.ai/api/docs/text-to-speech/overview)
- [Referência da API de Texto para Fala em Non-Streaming](https://murf.ai/api/docs/api-reference/text-to-speech/generate)