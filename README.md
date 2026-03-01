# JuntarPDFs

Automação em Python para:

- juntar vários PDFs na ordem desejada;
- **opcionalmente** inserir páginas/PDFs extras em posições específicas;
- usar por linha de comando ou por tela (interface gráfica);
- gerar executável com PyInstaller.

## Instalação

```bash
pip install -r requirements.txt
```

## Opção 1: usar com tela (GUI)

```bash
python app_gui.py
```

Na tela você consegue:

1. adicionar os PDFs base;
2. escolher se quer inserir páginas extras (opcional);
3. escolher o arquivo final;
4. gerar o PDF.

## Opção 2: usar por terminal

### Somente juntar PDFs

```bash
python juntar_pdfs.py arquivo1.pdf arquivo2.pdf -o saida.pdf
```

### Juntar e inserir páginas extras (opcional)

Formato de inserção: `POSICAO:arquivo.pdf`

```bash
python juntar_pdfs.py base1.pdf base2.pdf -o final.pdf \
  --insert 1:capa.pdf \
  --insert 3:assinatura.pdf
```

## Gerar executável (Windows)

```bash
pyinstaller --noconfirm --onefile --windowed --name JuntarPDFs app_gui.py
```

Executável gerado em:

- `dist/JuntarPDFs.exe`

## Observação sobre páginas com imagem e faixa branca

A junção/inserção copia as páginas diretamente do PDF original, sem rasterizar ou redimensionar, para evitar o problema de áreas em branco.
