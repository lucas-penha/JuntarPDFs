#!/usr/bin/env python3
"""Interface gráfica para juntar PDFs e enumerar páginas."""

from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from juntar_pdfs import CliError, NumberFormat, NumberPosition, merge_pdfs


class PdfMergeApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Juntar PDFs e Enumerar")
        self.root.geometry("900x620")
        self.root.resizable(True, True)

        self.input_files: list[Path] = []
        self._build_layout()

    # ------------------------------------------------------------------ layout

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
        self._build_options_section(container)
        self._build_output_section(container)
        self._build_progress_section(container)

    def _build_input_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="PDFs base (ordem final)", padding=12)
        frame.pack(fill="both", expand=True)

        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x", pady=(0, 8))

        ttk.Button(toolbar, text="➕ Adicionar PDFs", command=self._add_input_files).pack(side="left")
        ttk.Button(toolbar, text="🗑 Remover selecionado", command=self._remove_input).pack(
            side="left", padx=8
        )
        ttk.Button(toolbar, text="⬆ Mover para cima", command=lambda: self._move_input(-1)).pack(
            side="left"
        )
        ttk.Button(toolbar, text="⬇ Mover para baixo", command=lambda: self._move_input(1)).pack(
            side="left", padx=8
        )

        list_frame = ttk.Frame(frame)
        list_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        self.input_list = tk.Listbox(
            list_frame,
            height=10,
            yscrollcommand=scrollbar.set,
            activestyle="dotbox",
            selectbackground="#0078d4",
            selectforeground="white",
        )
        scrollbar.config(command=self.input_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.input_list.pack(fill="both", expand=True)

    def _build_options_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Opções de numeração", padding=12)
        frame.pack(fill="x", pady=(12, 0))

        # Formato
        fmt_frame = ttk.Frame(frame)
        fmt_frame.pack(side="left", padx=(0, 24))

        ttk.Label(fmt_frame, text="Formato:").pack(anchor="w")
        self.format_var = tk.StringVar(value="page_n")
        fmt_combo = ttk.Combobox(
            fmt_frame,
            textvariable=self.format_var,
            state="readonly",
            width=20,
        )
        fmt_combo["values"] = ["page_n", "n_of_total", "dash_n_dash", "number_only"]
        fmt_combo.pack()

        # Legenda de formatos
        ttk.Label(fmt_frame, text='page_n → "Página 1"', foreground="gray", font=("Segoe UI", 8)).pack(anchor="w")
        ttk.Label(fmt_frame, text='n_of_total → "1 / 10"', foreground="gray", font=("Segoe UI", 8)).pack(anchor="w")
        ttk.Label(fmt_frame, text='dash_n_dash → "- 1 -"', foreground="gray", font=("Segoe UI", 8)).pack(anchor="w")
        ttk.Label(fmt_frame, text='number_only → "1"', foreground="gray", font=("Segoe UI", 8)).pack(anchor="w")

        # Posição
        pos_frame = ttk.Frame(frame)
        pos_frame.pack(side="left", padx=(0, 24))

        ttk.Label(pos_frame, text="Posição:").pack(anchor="w")
        self.position_var = tk.StringVar(value="center")
        for val, label in [("left", "◀ Esquerda"), ("center", "● Centro"), ("right", "▶ Direita")]:
            ttk.Radiobutton(pos_frame, text=label, variable=self.position_var, value=val).pack(anchor="w")

        # Número inicial
        start_frame = ttk.Frame(frame)
        start_frame.pack(side="left")

        ttk.Label(start_frame, text="Número inicial:").pack(anchor="w")
        self.start_var = tk.IntVar(value=1)
        spin = ttk.Spinbox(start_frame, from_=1, to=9999, textvariable=self.start_var, width=8)
        spin.pack(anchor="w")

    def _build_output_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Saída", padding=12)
        frame.pack(fill="x", pady=(12, 0))

        self.output_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.output_var).pack(side="left", fill="x", expand=True)
        ttk.Button(frame, text="📂 Escolher saída", command=self._pick_output).pack(
            side="left", padx=8
        )
        self.generate_btn = ttk.Button(frame, text="🚀 Gerar PDF", command=self._generate)
        self.generate_btn.pack(side="left")

    def _build_progress_section(self, parent: ttk.Frame) -> None:
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=(10, 0))

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            frame, variable=self.progress_var, maximum=100, mode="determinate"
        )
        self.progress_bar.pack(fill="x")

        self.status_var = tk.StringVar(value="")
        ttk.Label(frame, textvariable=self.status_var, foreground="gray").pack(anchor="w", pady=(4, 0))

    # ------------------------------------------------------------------ actions

    def _add_input_files(self) -> None:
        selected = filedialog.askopenfilenames(
            title="Selecione os PDFs base",
            filetypes=[("PDF", "*.pdf")],
        )
        for file_path in selected:
            path = Path(file_path)
            self.input_files.append(path)
            # Exibe nome curto + diretório pai para melhor leitura
            short = f"{path.parent.name}/{path.name}"
            self.input_list.insert(tk.END, short)

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
            short = f"{path.parent.name}/{path.name}"
            self.input_list.insert(tk.END, short)
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

        # Desabilita o botão durante o processamento
        self.generate_btn.config(state="disabled")
        self.progress_var.set(0)
        self.status_var.set("Processando...")

        number_format: NumberFormat = self.format_var.get()  # type: ignore[assignment]
        position: NumberPosition = self.position_var.get()  # type: ignore[assignment]
        start_number: int = self.start_var.get()

        def progress_callback(done: int, total: int) -> None:
            pct = (done / total) * 100
            self.progress_var.set(pct)
            self.status_var.set(f"Processando página {done} de {total}…")
            self.root.update_idletasks()

        def run() -> None:
            try:
                merge_pdfs(
                    self.input_files,
                    Path(output_raw),
                    enumerate_pages=True,
                    number_format=number_format,
                    position=position,
                    start_number=start_number,
                    progress_callback=progress_callback,
                )
                self.root.after(0, self._on_success, output_raw)
            except CliError as exc:
                self.root.after(0, self._on_error, str(exc))

        threading.Thread(target=run, daemon=True).start()

    def _on_success(self, output_path: str) -> None:
        self.progress_var.set(100)
        self.status_var.set("Concluído!")
        self.generate_btn.config(state="normal")
        messagebox.showinfo("Sucesso", f"PDF gerado com sucesso em:\n{output_path}")

    def _on_error(self, message: str) -> None:
        self.progress_var.set(0)
        self.status_var.set("Erro ao gerar PDF.")
        self.generate_btn.config(state="normal")
        messagebox.showerror("Erro", message)


def main() -> None:
    root = tk.Tk()
    PdfMergeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()