# Gladia API - Obter Resultado da Transcrição - Versão: 2.0.0

## Visão Geral
Este documento descreve como obter o resultado de uma tarefa de transcrição de áudio pré-gravado utilizando a API da Gladia. O público-alvo são desenvolvedores que precisam verificar o status e recuperar a transcrição final de um arquivo de áudio submetido anteriormente.

## Pré-requisitos
- Conhecimento básico de como fazer requisições a uma API REST.
- Uma chave de API válida da Gladia (referida como `gladia-key`).
- Um `id` de transcrição válido, obtido após [iniciar uma tarefa de transcrição](gladia-api-transciption.md:1).

## Início Rápido
Para obter o resultado da sua transcrição, faça uma requisição `GET` para o endpoint `//v2/pre-recorded/{transcription_id}`, substituindo `{transcription_id}` pelo ID da sua tarefa.

```bash
curl --request GET \
  --url https://api.gladia.io/v2/pre-recorded/{id} \
  --header 'x-gladia-key: <api-key>'
```

## Exemplos

### Requisição com Go (http)
Veja como obter o resultado de uma transcrição usando o `http` em um ambiente Go.

```Go
package main

import (
	"fmt"
	"net/http"
	"io"
)

func main() {

	url := "https://api.gladia.io/v2/pre-recorded/{id}"

	req, _ := http.NewRequest("GET", url, nil)

	req.Header.Add("x-gladia-key", "<api-key>")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}
```

### Estrutura da Resposta de Sucesso (200 OK)
Se a requisição for bem-sucedida e a transcrição estiver completa, a API retornará um objeto JSON com o status `done` e o resultado detalhado. Enquanto o status for `queued` isso significa que o job ainda está sendo processado.

```json
{
  "id": "01J3QPA1YJ5Y9T...J7",
  "created_at": "2024-07-25T14:40:02.138Z",
  "updated_at": "2024-07-25T14:40:41.139Z",
  "status": "done",
  "result": {
    "metadata": {
      "audio_duration": 3600,
      "billing_time": 3600,
      "transcription_time": 20,
      // ... outras metadados
    },
    "transcription": {
      "full_transcript": "Este é um exemplo da transcrição completa do áudio.",
      "languages": [
        "fr"
      ],
      "utterances": [
        {
          "start": 0.5,
          "end": 4.2,
          "transcript": "Este é um exemplo",
          "words": [
            { "word": "Este", "start": 0.5, "end": 0.8 },
            { "word": "é", "start": 0.8, "end": 0.9 },
            { "word": "um", "start": 1.0, "end": 1.2 },
            { "word": "exemplo", "start": 1.3, "end": 2.1 }
          ]
        }
      ]
    }
  }
}
```

## Solução de Problemas
- **Problema**: Recebo um erro `404 Not Found`.
  - **Solução**: Verifique se o `id` da transcrição está correto e não expirou. Tarefas de transcrição e seus resultados são armazenados por um período limitado.

- **Problema**: Recebo um erro `401 Unauthorized`.
  - **Solução**: Certifique-se de que sua `x-gladia-key` está correta e incluída no header da requisição.

- **Problema**: O campo `status` na resposta é `queued`.
  - **Solução**: A transcrição ainda não foi concluída. Aguarde alguns instantes e faça a requisição novamente. O tempo de processamento depende da duração e qualidade do áudio.

## Documentos Relacionados
- [`Gladia API - Upload de Arquivo`](gladia-api-upload.md:1)
- [`Gladia API - Iniciar Transcrição`](gladia-api-transciption.md:1)
- [Documentação Oficial da API Gladia v2](https://docs.gladia.io/api-reference/v2/pre-recorded/get)