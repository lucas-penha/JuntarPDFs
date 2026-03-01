#!/usr/bin/env python3
"""Interface gráfica para juntar PDFs com inserções opcionais."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from juntar_pdfs import CliError, merge_pdfs


class PdfMergeApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Juntar PDFs")
        self.root.geometry("860x560")

        self.input_files: list[Path] = []
        self.insert_files: list[tuple[int, Path]] = []
        self.enable_insertions = tk.BooleanVar(value=False)

        self._build_layout()

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill="both", expand=True)

        header = ttk.Label(
            container,
            text="Automação para juntar PDFs",
            font=("Segoe UI", 14, "bold"),
        )
        header.pack(anchor="w")

        subtitle = ttk.Label(
            container,
            text=(
                "1) Adicione os PDFs base na ordem correta. "
                "2) Ative inserções apenas se quiser adicionar páginas extras."
            ),
        )
        subtitle.pack(anchor="w", pady=(4, 12))

        self._build_input_section(container)
        self._build_insertion_section(container)
        self._build_output_section(container)

    def _build_input_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="PDFs base (ordem final)", padding=12)
        frame.pack(fill="both", expand=True)

        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x", pady=(0, 8))

        ttk.Button(toolbar, text="Adicionar PDFs", command=self._add_input_files).pack(
            side="left"
        )
        ttk.Button(toolbar, text="Remover selecionado", command=self._remove_input).pack(
            side="left", padx=8
        )
        ttk.Button(toolbar, text="Mover para cima", command=lambda: self._move_input(-1)).pack(
            side="left"
        )
        ttk.Button(toolbar, text="Mover para baixo", command=lambda: self._move_input(1)).pack(
            side="left", padx=8
        )

        self.input_list = tk.Listbox(frame, height=8)
        self.input_list.pack(fill="both", expand=True)

    def _build_insertion_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Inserções (opcional)", padding=12)
        frame.pack(fill="both", expand=True, pady=(12, 0))

        check = ttk.Checkbutton(
            frame,
            text="Quero adicionar páginas/PDFs extras",
            variable=self.enable_insertions,
            command=self._toggle_insertion_controls,
        )
        check.pack(anchor="w")

        form = ttk.Frame(frame)
        form.pack(fill="x", pady=(8, 8))

        ttk.Label(form, text="Posição:").grid(row=0, column=0, sticky="w")
        self.position_entry = ttk.Entry(form, width=10)
        self.position_entry.grid(row=0, column=1, sticky="w", padx=(8, 16))
        ttk.Label(form, text="Arquivo extra:").grid(row=0, column=2, sticky="w")
        self.insert_file_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.insert_file_var).grid(
            row=0, column=3, sticky="ew", padx=8
        )
        ttk.Button(form, text="Selecionar", command=self._pick_insert_file).grid(
            row=0, column=4, sticky="w"
        )
        ttk.Button(form, text="Adicionar inserção", command=self._add_insertion).grid(
            row=0, column=5, sticky="w", padx=(8, 0)
        )
        form.columnconfigure(3, weight=1)

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=(0, 8))
        ttk.Button(
            buttons,
            text="Remover inserção selecionada",
            command=self._remove_insertion,
        ).pack(side="left")

        self.insert_list = tk.Listbox(frame, height=6)
        self.insert_list.pack(fill="both", expand=True)

        self._toggle_insertion_controls()

    def _build_output_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Saída", padding=12)
        frame.pack(fill="x", pady=(12, 0))

        self.output_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.output_var).pack(side="left", fill="x", expand=True)
        ttk.Button(frame, text="Escolher saída", command=self._pick_output).pack(
            side="left", padx=8
        )
        ttk.Button(frame, text="Gerar PDF", command=self._generate).pack(side="left")

    def _toggle_insertion_controls(self) -> None:
        state = "normal" if self.enable_insertions.get() else "disabled"
        self.position_entry.configure(state=state)
        self.insert_list.configure(state=state)

    def _add_input_files(self) -> None:
        selected = filedialog.askopenfilenames(
            title="Selecione os PDFs base",
            filetypes=[("PDF", "*.pdf")],
        )
        for file_path in selected:
            path = Path(file_path)
            self.input_files.append(path)
            self.input_list.insert(tk.END, str(path))

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

    def _pick_insert_file(self) -> None:
        selected = filedialog.askopenfilename(
            title="Selecione PDF extra",
            filetypes=[("PDF", "*.pdf")],
        )
        if selected:
            self.insert_file_var.set(selected)

    def _add_insertion(self) -> None:
        if not self.enable_insertions.get():
            messagebox.showwarning("Inserções", "Ative a opção de inserções para adicionar.")
            return

        raw_position = self.position_entry.get().strip()
        raw_path = self.insert_file_var.get().strip()

        if not raw_position or not raw_path:
            messagebox.showwarning("Inserções", "Informe posição e arquivo extra.")
            return

        try:
            position = int(raw_position)
            if position < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Inserções", "A posição precisa ser um número inteiro >= 1.")
            return

        path = Path(raw_path)
        if not path.exists() or not path.is_file():
            messagebox.showerror("Inserções", "Arquivo extra não encontrado.")
            return

        self.insert_files.append((position, path))
        self.insert_list.insert(tk.END, f"Posição {position}: {path}")
        self.position_entry.delete(0, tk.END)
        self.insert_file_var.set("")

    def _remove_insertion(self) -> None:
        index = self.insert_list.curselection()
        if not index:
            return
        idx = index[0]
        self.insert_list.delete(idx)
        self.insert_files.pop(idx)

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
            messagebox.showerror("Erro", "Adicione pelo menos 1 PDF base.")
            return
        if not output_raw:
            messagebox.showerror("Erro", "Escolha o arquivo de saída.")
            return

        try:
            insertions = self.insert_files if self.enable_insertions.get() else []
            merge_pdfs(self.input_files, Path(output_raw), insertions)
        except CliError as exc:
            messagebox.showerror("Erro", str(exc))
            return
        except ModuleNotFoundError:
            messagebox.showerror(
                "Dependência ausente",
                "Instale as dependências com: pip install -r requirements.txt",
            )
            return

        messagebox.showinfo("Sucesso", f"PDF gerado com sucesso em:\n{output_raw}")


def main() -> None:
    root = tk.Tk()
    PdfMergeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
