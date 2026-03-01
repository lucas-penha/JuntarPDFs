#!/usr/bin/env python3
"""Interface gráfica para juntar PDFs e enumerar páginas."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from juntar_pdfs import CliError, merge_pdfs


class PdfMergeApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Juntar PDFs e Enumerar")
        self.root.geometry("860x520")

        self.input_files: list[Path] = []
        self._build_layout()

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text="Juntar PDFs e enumerar páginas",
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w")

        ttk.Label(
            container,
            text="Adicione os PDFs na ordem final. O arquivo gerado terá numeração de páginas no rodapé.",
        ).pack(anchor="w", pady=(4, 12))

        self._build_input_section(container)
        self._build_output_section(container)

    def _build_input_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="PDFs base (ordem final)", padding=12)
        frame.pack(fill="both", expand=True)

        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x", pady=(0, 8))

        ttk.Button(toolbar, text="Adicionar PDFs", command=self._add_input_files).pack(side="left")
        ttk.Button(toolbar, text="Remover selecionado", command=self._remove_input).pack(
            side="left", padx=8
        )
        ttk.Button(toolbar, text="Mover para cima", command=lambda: self._move_input(-1)).pack(
            side="left"
        )
        ttk.Button(toolbar, text="Mover para baixo", command=lambda: self._move_input(1)).pack(
            side="left", padx=8
        )
        ttk.Button(toolbar, text="Limpar lista", command=self._clear_inputs).pack(side="left")

        self.input_list = tk.Listbox(frame, height=12)
        self.input_list.pack(fill="both", expand=True)

    def _build_output_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Saída", padding=12)
        frame.pack(fill="x", pady=(12, 0))

        self.output_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.output_var).pack(side="left", fill="x", expand=True)
        ttk.Button(frame, text="Escolher saída", command=self._pick_output).pack(
            side="left", padx=8
        )
        ttk.Button(frame, text="Gerar PDF", command=self._generate).pack(side="left")

    def _add_input_files(self) -> None:
        selected = filedialog.askopenfilenames(
            title="Selecione os PDFs base",
            filetypes=[("PDF", "*.pdf")],
        )
        for file_path in selected:
            path = Path(file_path)
            if path in self.input_files:
                continue
            self.input_files.append(path)
            self.input_list.insert(tk.END, str(path))

    def _clear_inputs(self) -> None:
        self.input_files.clear()
        self.input_list.delete(0, tk.END)

    def _remove_input(self) -> None:
        index = self.input_list.curselection()
        if not index:
            return
        idx = index[0]
        self.input_list.delete(idx)
        self.input_files.pop(idx)

    def _move_input(self, direction: int) -> None:
        index = self.input_list.curselection()
        if not index:
            return

        old_idx = index[0]
        new_idx = old_idx + direction
        if new_idx < 0 or new_idx >= len(self.input_files):
            return

        self.input_files[old_idx], self.input_files[new_idx] = (
            self.input_files[new_idx],
            self.input_files[old_idx],
        )
        self._refresh_input_list(new_idx)

    def _refresh_input_list(self, selected_index: int | None = None) -> None:
        self.input_list.delete(0, tk.END)
        for path in self.input_files:
            self.input_list.insert(tk.END, str(path))
        if selected_index is not None:
            self.input_list.selection_set(selected_index)

    def _pick_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Salvar PDF final",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
        )
        if path:
            self.output_var.set(path)

    def _generate(self) -> None:
        output_raw = self.output_var.get().strip()

        if not self.input_files:
            messagebox.showerror("Erro", "Adicione pelo menos 1 PDF.")
            return
        if not output_raw:
            messagebox.showerror("Erro", "Escolha o arquivo de saída.")
            return

        try:
            merge_pdfs(self.input_files, Path(output_raw), enumerate_pages=True)
        except CliError as exc:
            messagebox.showerror("Erro", str(exc))
            return

        messagebox.showinfo("Sucesso", f"PDF gerado com sucesso em:\n{output_raw}")


def main() -> None:
    root = tk.Tk()
    PdfMergeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
