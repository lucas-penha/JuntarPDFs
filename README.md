# JuntarPDFs

Automação em Python para:

- juntar vários PDFs na ordem desejada;
- enumerar todas as páginas no PDF final;
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
2. organizar a ordem;
3. escolher o arquivo final;
4. gerar o PDF com páginas enumeradas no rodapé.

## Opção 2: usar por terminal

```bash
python juntar_pdfs.py arquivo1.pdf arquivo2.pdf arquivo3.pdf -o saida.pdf
```

> O PDF gerado já sai com numeração contínua de páginas (Página 1, Página 2, ...).

## Gerar executável (Windows)

```bash
pyinstaller --noconfirm --onefile --windowed --name JuntarPDFs app_gui.py
```

Executável gerado em:

- `dist/JuntarPDFs.exe`
