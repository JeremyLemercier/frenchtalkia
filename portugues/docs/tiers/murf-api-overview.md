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
    text="Há muito a ser dito",
    voice_id="en-US-terrell",
)

print(res.audio_file)
```

## Exemplos

### Formatos de Saída Suportados
A API suporta múltiplos formatos de saída para o áudio gerado - o formato padrão é WAV:

| Formato | Descrição |
|---------|------------|
| **WAV** | Formato de áudio não comprimido, útil para aplicações de baixa latência |
| **MP3** | Formato de áudio comprimido, amplamente suportado e adequado para aplicações onde o tamanho do arquivo é uma preocupação |
| **FLAC** | Formato de áudio comprimido sem perdas, ideal para aplicações que exigem alta fidelidade de áudio |
| **ALAW** | Formato de áudio comprimido comumente usado em telefonia |
| **ULAW** | Outro formato de áudio comprimido usado em telefonia |

### Especificando Formato de Saída
```python
from murf import Murf

client = Murf()
res = client.text_to_speech.generate(
    text="Olá, como você está hoje?",
    voice_id="en-US-julia",
    format="MP3",
    channel_type="STEREO",
    sample_rate=44100
)
```

### Codificação Base64
Você pode receber o arquivo de áudio em formato codificado Base64:
```python
from murf import Murf

client = Murf()
res = client.text_to_speech.generate(
    text="Olá, como você está hoje?",
    voice_id="en-US-julia",
    encode_as_base_64=True
)
```

A resposta incluira o arquivo audio codificado em Base64, para ser decodificado e usado em sua aplicação:
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

client.text_to_speech.generate(
    text="Olá, como você está hoje?",
    voice_id="en-US-natalie",
    encode_as_base_64=True,
    request_options={
        'additional_headers': {
            'accept-encoding': 'gzip'
        }
    }
)
```

## Solução de Problemas
- **Problema**: Formatos ULAW e ALAW suportam apenas canal mono e taxa de amostragem de 8000 Hz → **Solução**: Se especificar tipo de canal ou taxa de amostragem diferente, a API usará os valores suportados
- **Problema**: Arquivo de áudio não está disponível → **Solução**: Verifique se o link expirou (arquivos ficam disponíveis por 72 horas após a geração)
- **Problema**: Erro de autenticação → **Solução**: Verifique se sua chave de API está correta e definida como variável de ambiente MURF_API_KEY

## Documentos Relacionados
- [Documentação da API Murf](https://murf.ai/api/docs)
- [Referência da API de Texto para Fala](https://murf.ai/api/docs/text-to-speech/overview)
- [Painel de API Murf](https://murf.ai/api/dashboard)