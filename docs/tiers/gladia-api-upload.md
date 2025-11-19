# API Gladia: Endpoint de Upload Pré-gravado - Versão: 2.0.0

## Visão Geral
Este documento descreve o endpoint da API da Gladia para o upload de arquivos de áudio ou vídeo. Destina-se a desenvolvedores que necessitam enviar mídias para processamento de transcrição pré-gravada.

O endpoint permite o envio de arquivos da maneira seguinte:
**Upload Direto**: Enviando o arquivo de áudio/vídeo como `multipart/form-data`.

## Pré-requisitos
**Chave de API**: É necessário ter uma chave de API da Gladia (`x-gladia-key`) para autenticar as requisições.

## Início Rápido

Para fazer o upload de um arquivo, você pode utilizar `curl`. Abaixo estão exemplos para upload direto e via URL.

### Exemplo de Upload Direto de Arquivo (versão cURL)
```bash
curl --request POST \
  --url https://api.gladia.io/v2/upload \
  --header 'Content-Type: multipart/form-data' \
  --header 'x-gladia-key: <api-key>' \
  --form audio=@example-file
```

### Exemplo de Upload Direto de Arquivo (versão Go)
```Go
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://api.gladia.io/v2/upload"

	payload := strings.NewReader("-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"audio\"\r\n\r\n{\n  \"fileName\": \"example-file\"\n}\r\n-----011000010111000001101001--\r\n\r\n")

	req, _ := http.NewRequest("POST", url, payload)

	req.Header.Add("x-gladia-key", "<api-key>")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}
```

## Detalhes do Endpoint

-   **Método**: `POST`
-   **URL**: `https://api.gladia.io/v2/upload`

### Autenticação
A autenticação é feita através do cabeçalho (`Header`) da requisição, utilizando sua chave de API.

-   **Cabeçalho**: `x-gladia-key`
-   **Valor**: `Sua Chave de API da Gladia`

### Corpo da Requisição (Body)

-   `multipart/form-data` (Para upload de arquivo)
-   **`audio`** (obrigatório): O arquivo de áudio ou vídeo a ser enviado.
    -   Tipo: `string` (binary)
    -   Descrição: O arquivo que será processado.

### Resposta de Sucesso (200 OK)

Se o upload for bem-sucedido, a API retornará um objeto JSON com a URL do arquivo na Gladia e seus metadados.

```json
{
  "audio_url": "https://api.gladia.io/file/6c09400e-23d2-4bd2-be55-96a5ececfa3b",
  "audio_metadata": {
    "id": "6c09400e-23d2-4bd2-be55-96a5ececfa3b",
    "filename": "short-audio-en-16000.wav",
    "source": "http://files.gladia.io/example/audio-transcription/split_infinity.wav",
    "extension": "wav",
    "size": 365702,
    "audio_duration": 4.145782,
    "number_of_channels": 1
  }
}
```

#### Campos da Resposta:

-   `audio_url` (string): A URL interna da Gladia para o arquivo enviado. Esta URL pode ser usada em outras requisições da API.
-   `audio_metadata` (object): Um objeto contendo os metadados detectados do arquivo de áudio.
    -   `id` (string): O ID único do arquivo.
    -   `filename` (string): O nome do arquivo original.
    -   `source` (string): A fonte do áudio (URL, no caso de upload por link).
    -   `extension` (string): A extensão do arquivo detectada.
    -   `size` (integer): O tamanho do arquivo em bytes.
    -   `audio_duration` (number): A duração do áudio em segundos.
    -   `number_of_channels` (integer): O número de canais de áudio.

## Solução de Problemas

-   **Problema**: Recebendo erro de autenticação (`401 Unauthorized`).
    -   **Solução**: Verifique se a sua `x-gladia-key` está correta e se foi incluída no cabeçalho da requisição.

-   **Problema**: Erro ao enviar um arquivo local (`curl: (26) Failed to open/read`).
    -   **Solução**: Certifique-se de que o caminho para o arquivo após `@` está correto e que o arquivo existe no diretório especificado.

-   **Problema**: A requisição falha com um erro de corpo malformado.
    -   **Solução**: Garanta que o `Content-Type` no cabeçalho corresponde ao formato do corpo da sua requisição (`multipart/form-data` para upload de arquivo).

## Documentos Relacionados
- [Documentação Oficial da Gladia API v2](https://docs.gladia.io/api-reference/v2)
