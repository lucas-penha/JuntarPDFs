#!/usr/bin/env python3
"""Automação simples para juntar PDFs e, opcionalmente, inserir páginas extras."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable



class CliError(Exception):
    """Erro de validação de argumentos para mensagens amigáveis."""


def _parse_insert_item(raw: str) -> tuple[int, Path]:
    """Converte argumento no formato POSICAO:arquivo.pdf."""
    if ":" not in raw:
        raise CliError(
            f"Formato inválido em '{raw}'. Use POSICAO:arquivo.pdf (ex.: 3:extra.pdf)."
        )

    raw_position, raw_path = raw.split(":", 1)
    try:
        position = int(raw_position)
    except ValueError as exc:
        raise CliError(f"Posição inválida em '{raw}'.") from exc

    if position < 1:
        raise CliError(f"A posição precisa ser >= 1 em '{raw}'.")

    page_path = Path(raw_path)
    if not page_path.exists() or not page_path.is_file():
        raise CliError(f"PDF extra não encontrado: {page_path}")

    return position, page_path


def _read_pages(pdf_path: Path):
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    return list(reader.pages)


def _validate_inputs(paths: Iterable[Path]) -> None:
    for path in paths:
        if not path.exists() or not path.is_file():
            raise CliError(f"Arquivo não encontrado: {path}")


def merge_pdfs(
    inputs: list[Path],
    output: Path,
    insertions: list[tuple[int, Path]] | None = None,
) -> None:
    """Junta PDFs na ordem informada e insere páginas extras quando solicitado.

    Estratégia para evitar páginas com 'faixa branca':
    - As páginas extras são copiadas diretamente do PDF original (sem rasterizar,
      sem redimensionar e sem conversão para imagem).
    """
    insertions = insertions or []

    _validate_inputs(inputs)

    for _, extra_pdf in insertions:
        _validate_inputs([extra_pdf])

    base_pages = []
    for pdf_path in inputs:
        base_pages.extend(_read_pages(pdf_path))

    max_position = len(base_pages) + 1
    for position, _ in insertions:
        if position > max_position:
            raise CliError(
                f"Posição {position} é maior que o total permitido ({max_position})."
            )

    # Ordena para inserções previsíveis (da menor posição para a maior)
    ordered_insertions = sorted(insertions, key=lambda item: item[0])

    from pypdf import PdfWriter

    writer = PdfWriter()
    current_base_index = 0

    for position, extra_pdf in ordered_insertions:
        target_index = position - 1

        while current_base_index < target_index and current_base_index < len(base_pages):
            writer.add_page(base_pages[current_base_index])
            current_base_index += 1

        extra_pages = _read_pages(extra_pdf)
        for page in extra_pages:
            writer.add_page(page)

    while current_base_index < len(base_pages):
        writer.add_page(base_pages[current_base_index])
        current_base_index += 1

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as stream:
        writer.write(stream)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Junta PDFs e permite inserir páginas extras em posições específicas, "
            "com opção de não inserir nada."
        )
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        type=Path,
        help="Lista de PDFs de entrada na ordem desejada.",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        type=Path,
        help="Arquivo PDF de saída.",
    )
    parser.add_argument(
        "--insert",
        action="append",
        default=[],
        metavar="POSICAO:ARQUIVO",
        help=(
            "Insere um PDF extra na posição indicada (1 = antes da primeira página). "
            "Pode ser usado várias vezes. Ex.: --insert 2:capa.pdf"
        ),
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        insertions = [_parse_insert_item(item) for item in args.insert]
        merge_pdfs(inputs=args.inputs, output=args.output, insertions=insertions)
    except CliError as exc:
        parser.error(str(exc))
        return 2

    print(f"PDF gerado com sucesso: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
