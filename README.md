# JuntarPDFs

Automação simples em Python para:

- juntar vários PDFs na ordem desejada;
- **opcionalmente** inserir páginas/PDFs extras em posições específicas;
- preservar o conteúdo original das páginas (incluindo imagens), sem redimensionar/rasterizar.

## Requisitos

- Python 3.10+
- Dependências:

```bash
pip install -r requirements.txt
```

## Uso básico (somente juntar PDFs)

```bash
python juntar_pdfs.py arquivo1.pdf arquivo2.pdf arquivo3.pdf -o saida.pdf
```

## Inserir páginas extras (opcional)

Você pode repetir `--insert` quantas vezes quiser no formato:

`POSICAO:arquivo.pdf`

- `1` = insere antes da primeira página do PDF final.
- `2` = insere antes da segunda página, e assim por diante.

Exemplo:

```bash
python juntar_pdfs.py contrato.pdf anexo.pdf -o final.pdf \
  --insert 1:capa.pdf \
  --insert 3:assinatura.pdf
```

## Observação sobre páginas com imagem e faixa branca

Para evitar o problema de parte em branco ao adicionar páginas com imagem,
a automação copia as páginas diretamente do PDF original, sem converter para imagem
ou ajustar escala manualmente.
