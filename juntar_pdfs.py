#!/usr/bin/env python3
"""Automação simples para juntar PDFs e enumerar páginas."""

from __future__ import annotations

import argparse
import io
from pathlib import Path
from typing import Iterable


class CliError(Exception):
    """Erro de validação de argumentos para mensagens amigáveis."""


def _validate_inputs(paths: Iterable[Path]) -> None:
    for path in paths:
        if not path.exists() or not path.is_file():
            raise CliError(f"Arquivo não encontrado: {path}")


def _build_number_overlay(width: float, height: float, page_number: int):
    from pypdf import PdfReader
    from reportlab.lib.colors import Color
    from reportlab.pdfgen import canvas

    stream = io.BytesIO()
    page_canvas = canvas.Canvas(stream, pagesize=(width, height))
    page_canvas.setFillColor(Color(0.25, 0.25, 0.25, alpha=1))
    page_canvas.setFont("Helvetica", 10)
    page_canvas.drawCentredString(width / 2, 14, f"Página {page_number}")
    page_canvas.save()
    stream.seek(0)

    return PdfReader(stream).pages[0]


def merge_pdfs(inputs: list[Path], output: Path, enumerate_pages: bool = True) -> None:
    """Junta PDFs na ordem informada e enumera as páginas no rodapé."""
    _validate_inputs(inputs)

    try:
        from pypdf import PdfReader, PdfWriter
    except ModuleNotFoundError as exc:
        raise CliError("Dependência ausente: instale com `pip install -r requirements.txt`.") from exc

    writer = PdfWriter()

    global_page_number = 1
    for pdf_path in inputs:
        reader = PdfReader(str(pdf_path))

        for page in reader.pages:
            if enumerate_pages:
                width = float(page.mediabox.width)
                height = float(page.mediabox.height)
                overlay = _build_number_overlay(width, height, global_page_number)
                page.merge_page(overlay)

            writer.add_page(page)
            global_page_number += 1

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as stream:
        writer.write(stream)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Junta PDFs na ordem informada e enumera todas as páginas no rodapé."
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
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        merge_pdfs(inputs=args.inputs, output=args.output, enumerate_pages=True)
    except CliError as exc:
        parser.error(str(exc))
        return 2

    print(f"PDF gerado com sucesso: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
