#!/usr/bin/env python3
"""Automação simples para juntar PDFs e enumerar páginas."""

from __future__ import annotations

import argparse
import io
from pathlib import Path
from typing import Callable, Iterable, Literal

NumberFormat = Literal["page_n", "n_of_total", "dash_n_dash", "number_only"]
NumberPosition = Literal["left", "center", "right"]


class CliError(Exception):
    """Erro de validação de argumentos para mensagens amigáveis."""


def _validate_inputs(paths: Iterable[Path]) -> None:
    for path in paths:
        if not path.exists() or not path.is_file():
            raise CliError(f"Arquivo não encontrado: {path}")


def _format_page_label(number_format: NumberFormat, page_number: int, total_pages: int) -> str:
    if number_format == "page_n":
        return f"Página {page_number}"
    elif number_format == "n_of_total":
        return f"{page_number} / {total_pages}"
    elif number_format == "dash_n_dash":
        return f"- {page_number} -"
    else:  # number_only
        return str(page_number)


def _build_number_overlay(
    width: float,
    height: float,
    page_number: int,
    total_pages: int,
    number_format: NumberFormat,
    position: NumberPosition,
):
    from pypdf import PdfReader
    from reportlab.lib.colors import Color
    from reportlab.pdfgen import canvas

    label = _format_page_label(number_format, page_number, total_pages)

    stream = io.BytesIO()
    page_canvas = canvas.Canvas(stream, pagesize=(width, height))
    page_canvas.setFillColor(Color(0.25, 0.25, 0.25, alpha=1))
    page_canvas.setFont("Helvetica", 10)

    margin = 36
    y = 14

    if position == "left":
        page_canvas.drawString(margin, y, label)
    elif position == "right":
        page_canvas.drawRightString(width - margin, y, label)
    else:  # center
        page_canvas.drawCentredString(width / 2, y, label)

    page_canvas.save()
    stream.seek(0)
    return PdfReader(stream).pages[0]


def merge_pdfs(
    inputs: list[Path],
    output: Path,
    enumerate_pages: bool = True,
    number_format: NumberFormat = "page_n",
    position: NumberPosition = "center",
    start_number: int = 1,
    progress_callback: Callable[[int, int], None] | None = None,
) -> None:
    """Junta PDFs na ordem informada e enumera as páginas no rodapé."""
    _validate_inputs(inputs)

    try:
        from pypdf import PdfReader, PdfWriter
    except ModuleNotFoundError as exc:
        raise CliError("Dependência ausente: instale com `pip install -r requirements.txt`.") from exc

    writer = PdfWriter()

    # Pré-calcula total de páginas para o formato "n / total"
    total_pages = 0
    readers: list[PdfReader] = []
    for pdf_path in inputs:
        reader = PdfReader(str(pdf_path))
        readers.append(reader)
        total_pages += len(reader.pages)

    global_page_number = start_number
    processed = 0

    for reader in readers:
        for page in reader.pages:
            if enumerate_pages:
                width = float(page.mediabox.width)
                height = float(page.mediabox.height)
                overlay = _build_number_overlay(
                    width, height, global_page_number, total_pages, number_format, position
                )
                page.merge_page(overlay)

            writer.add_page(page)
            global_page_number += 1
            processed += 1

            if progress_callback:
                progress_callback(processed, total_pages)

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
    parser.add_argument(
        "--format",
        dest="number_format",
        choices=["page_n", "n_of_total", "dash_n_dash", "number_only"],
        default="page_n",
        help="Formato da numeração (padrão: page_n).",
    )
    parser.add_argument(
        "--position",
        choices=["left", "center", "right"],
        default="center",
        help="Posição do número no rodapé (padrão: center).",
    )
    parser.add_argument(
        "--start",
        dest="start_number",
        type=int,
        default=1,
        help="Número inicial de página (padrão: 1).",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        merge_pdfs(
            inputs=args.inputs,
            output=args.output,
            enumerate_pages=True,
            number_format=args.number_format,
            position=args.position,
            start_number=args.start_number,
        )
    except CliError as exc:
        parser.error(str(exc))
        return 2

    print(f"PDF gerado com sucesso: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())