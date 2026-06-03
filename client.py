"""
Patrón Command — Cliente (Interfaz Gráfica con Tkinter)
Editor de texto interactivo con Write, Delete, Copy, Cut, Paste, Undo, Redo.
Se escribe directamente en el área de texto y se selecciona con el mouse.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from text_editor import TextEditor
from commands import (
    WriteCommand,
    DeleteCommand,
    CopyCommand,
    CutCommand,
    PasteCommand,
)
from invoker import TextEditorInvoker


class Client:
    """Client — Interfaz gráfica que conecta la UI con el patrón Command."""

    # ── colores (Catppuccin Mocha) ──────────────────────────────
    BG        = "#1e1e2e"
    SURFACE   = "#313244"
    OVERLAY   = "#45475a"
    TEXT_CLR  = "#cdd6f4"
    SUBTEXT   = "#a6adc8"
    BLUE      = "#89b4fa"
    GREEN     = "#a6e3a1"
    YELLOW    = "#f9e2af"
    PINK      = "#f5c2e7"
    TEAL      = "#94e2d5"
    RED       = "#f38ba8"
    MAUVE     = "#cba6f7"

    def __init__(self):
        self._editor = TextEditor()
        self._invoker = TextEditorInvoker()
        self._syncing = False  # evita recursión al sincronizar

        # ── Ventana ─────────────────────────────────────────────
        self._root = tk.Tk()
        self._root.title("Patrón Command — Editor de Texto")
        self._root.geometry("900x640")
        self._root.configure(bg=self.BG)
        self._root.minsize(750, 550)

        self._setup_styles()
        self._build_ui()
        self._bind_shortcuts()

    # ═══════════════════════════════════════════════════════════
    #  Estilos
    # ═══════════════════════════════════════════════════════════

    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use("clam")

        s.configure("Title.TLabel",
                     font=("Segoe UI", 15, "bold"),
                     foreground=self.TEXT_CLR, background=self.BG)

        s.configure("Sub.TLabel",
                     font=("Segoe UI", 9),
                     foreground=self.SUBTEXT, background=self.BG)

        s.configure("Section.TLabelframe",
                     background=self.BG)
        s.configure("Section.TLabelframe.Label",
                     font=("Segoe UI", 9, "bold"),
                     foreground=self.BLUE, background=self.BG)

        for name, bg, fg, active_bg in [
            ("Write.TButton",  self.BLUE,   self.BG, self.TEAL),
            ("Delete.TButton", self.RED,    "#fff",  self.PINK),
            ("Copy.TButton",   self.MAUVE,  self.BG, self.PINK),
            ("Cut.TButton",    self.YELLOW, self.BG, self.GREEN),
            ("Paste.TButton",  self.GREEN,  self.BG, self.TEAL),
            ("Undo.TButton",   self.YELLOW, self.BG, self.PINK),
            ("Redo.TButton",   self.TEAL,   self.BG, self.GREEN),
        ]:
            s.configure(name, font=("Segoe UI", 9, "bold"),
                        foreground=fg, background=bg, padding=(12, 7))
            s.map(name, background=[("active", active_bg)])

    # ═══════════════════════════════════════════════════════════
    #  Construcción de la UI
    # ═══════════════════════════════════════════════════════════

    def _build_ui(self):
        # ── Header ──────────────────────────────────────────────
        header = tk.Frame(self._root, bg=self.BG)
        header.pack(fill="x", padx=20, pady=(14, 4))

        ttk.Label(header, text="✏️  Editor de Texto — Patrón Command",
                  style="Title.TLabel").pack(side="left")

        ttk.Label(header,
                  text="Escribe directamente · Selecciona con el mouse · Usa los botones o atajos",
                  style="Sub.TLabel").pack(side="left", padx=(16, 0))

        # ── Toolbar ─────────────────────────────────────────────
        toolbar = tk.Frame(self._root, bg=self.SURFACE, pady=6)
        toolbar.pack(fill="x", padx=20, pady=(6, 0))

        for text, style, cmd in [
            ("📝 Write (Enter)",  "Write.TButton",  self._on_write),
            ("🗑️ Delete (Del)",   "Delete.TButton", self._on_delete),
            ("📋 Copy (Ctrl+C)",  "Copy.TButton",   self._on_copy),
            ("✂️ Cut (Ctrl+X)",   "Cut.TButton",    self._on_cut),
            ("📌 Paste (Ctrl+V)", "Paste.TButton",  self._on_paste),
        ]:
            ttk.Button(toolbar, text=text, style=style,
                       command=cmd).pack(side="left", padx=4)

        # separador visual
        tk.Frame(toolbar, width=2, bg=self.OVERLAY).pack(side="left",
                                                          fill="y", padx=8, pady=2)

        ttk.Button(toolbar, text="⬅️ Undo (Ctrl+Z)", style="Undo.TButton",
                   command=self._on_undo).pack(side="left", padx=4)
        ttk.Button(toolbar, text="➡️ Redo (Ctrl+Y)", style="Redo.TButton",
                   command=self._on_redo).pack(side="left", padx=4)

        # ── Cuerpo principal ────────────────────────────────────
        body = tk.PanedWindow(self._root, orient="horizontal",
                              bg=self.OVERLAY, sashwidth=4)
        body.pack(fill="both", expand=True, padx=20, pady=10)

        # --- Área de texto (izquierda) ---
        text_frame = ttk.LabelFrame(body, text=" Editor ",
                                     style="Section.TLabelframe")
        body.add(text_frame, width=520)

        self._text_widget = tk.Text(
            text_frame, font=("Consolas", 13), wrap="word",
            bg=self.SURFACE, fg=self.TEXT_CLR, insertbackground=self.TEAL,
            selectbackground=self.BLUE, selectforeground=self.BG,
            relief="flat", padx=12, pady=10, undo=False,
        )
        self._text_widget.pack(fill="both", expand=True, padx=8, pady=8)

        # --- Panel derecho ---
        right = tk.Frame(body, bg=self.BG)
        body.add(right, width=320)

        # Clipboard
        clip_frame = ttk.LabelFrame(right, text=" 📋 Clipboard ",
                                     style="Section.TLabelframe")
        clip_frame.pack(fill="x", padx=4, pady=(4, 6))

        self._clip_label = tk.Label(
            clip_frame, text="(vacío)", font=("Consolas", 10),
            fg=self.PINK, bg=self.SURFACE, anchor="w",
            padx=8, pady=6, wraplength=260, justify="left",
        )
        self._clip_label.pack(fill="x", padx=8, pady=6)

        # Historial
        hist_frame = ttk.LabelFrame(right, text=" 📜 Historial de Comandos ",
                                     style="Section.TLabelframe")
        hist_frame.pack(fill="both", expand=True, padx=4, pady=(0, 6))

        hist_scroll = tk.Scrollbar(hist_frame)
        hist_scroll.pack(side="right", fill="y", pady=6, padx=(0, 6))

        self._history_list = tk.Listbox(
            hist_frame, font=("Consolas", 9),
            bg=self.SURFACE, fg=self.GREEN,
            selectbackground=self.OVERLAY, relief="flat",
            yscrollcommand=hist_scroll.set,
        )
        self._history_list.pack(fill="both", expand=True, padx=(8, 0), pady=6)
        hist_scroll.config(command=self._history_list.yview)

        # Log
        log_frame = ttk.LabelFrame(right, text=" 💬 Log ",
                                    style="Section.TLabelframe")
        log_frame.pack(fill="x", padx=4, pady=(0, 4))

        self._log_label = tk.Label(
            log_frame, text="Listo. Escribe algo en el editor.",
            font=("Segoe UI", 9), fg=self.TEAL, bg=self.SURFACE,
            anchor="w", padx=8, pady=5, wraplength=280, justify="left",
        )
        self._log_label.pack(fill="x", padx=8, pady=6)

        # ── Status bar ─────────────────────────────────────────
        self._status = tk.Label(
            self._root, text="Pos: 0  |  Sel: ninguna  |  Chars: 0",
            font=("Segoe UI", 8), fg=self.SUBTEXT, bg=self.OVERLAY,
            anchor="w", padx=12, pady=3,
        )
        self._status.pack(fill="x", side="bottom")

    # ═══════════════════════════════════════════════════════════
    #  Atajos de teclado
    # ═══════════════════════════════════════════════════════════

    def _bind_shortcuts(self):
        w = self._text_widget

        # Interceptar escritura carácter a carácter
        w.bind("<Key>", self._on_key)

        # Interceptar Backspace
        w.bind("<BackSpace>", self._on_backspace)

        # Atajos estándar
        w.bind("<Control-c>", lambda e: (self._on_copy(), "break")[1])
        w.bind("<Control-x>", lambda e: (self._on_cut(), "break")[1])
        w.bind("<Control-v>", lambda e: (self._on_paste(), "break")[1])
        w.bind("<Control-z>", lambda e: (self._on_undo(), "break")[1])
        w.bind("<Control-y>", lambda e: (self._on_redo(), "break")[1])
        w.bind("<Delete>",    lambda e: (self._on_delete_key(), "break")[1])

        # Actualizar status bar al mover cursor / seleccionar
        w.bind("<ButtonRelease-1>", lambda e: self._update_status())
        w.bind("<KeyRelease>", lambda e: self._update_status())

    # ═══════════════════════════════════════════════════════════
    #  Helpers
    # ═══════════════════════════════════════════════════════════

    def _cursor_pos(self) -> int:
        """Retorna la posición del cursor como índice entero."""
        idx = self._text_widget.index("insert")
        line, col = map(int, idx.split("."))
        # Contar caracteres hasta la línea + columna
        content = self._text_widget.get("1.0", "end-1c")
        lines = content.split("\n")
        pos = sum(len(lines[i]) + 1 for i in range(line - 1)) + col
        return pos

    def _selection_range(self):
        """Retorna (start, length) de la selección o None."""
        try:
            sel_start = self._text_widget.index("sel.first")
            sel_end = self._text_widget.index("sel.last")

            content = self._text_widget.get("1.0", "end-1c")

            def idx_to_int(idx_str):
                line, col = map(int, idx_str.split("."))
                lines = content.split("\n")
                return sum(len(lines[i]) + 1 for i in range(line - 1)) + col

            start = idx_to_int(sel_start)
            end = idx_to_int(sel_end)
            return start, end - start
        except tk.TclError:
            return None

    def _log(self, msg: str):
        self._log_label.config(text=msg)

    def _ensure_sync(self):
        """Sincroniza el TextEditor desde el widget si están desfasados."""
        widget_text = self._text_widget.get("1.0", "end-1c")
        editor_text = self._editor.get_text()
        if widget_text != editor_text:
            # El widget tiene texto que el modelo no conoce.
            # Crear comandos para ponerlo al día.
            if editor_text:
                del_cmd = DeleteCommand(self._editor, 0, len(editor_text))
                self._invoker.execute_command(del_cmd)
            if widget_text:
                write_cmd = WriteCommand(self._editor, 0, widget_text)
                self._invoker.execute_command(write_cmd)

    def _sync_widget_from_editor(self):
        """Sincroniza el widget de texto con el estado del TextEditor."""
        self._syncing = True
        cursor = self._text_widget.index("insert")
        self._text_widget.delete("1.0", "end")
        self._text_widget.insert("1.0", self._editor.get_text())
        # Restaurar cursor
        try:
            self._text_widget.mark_set("insert", cursor)
        except tk.TclError:
            self._text_widget.mark_set("insert", "end")
        self._syncing = False

    def _refresh_panels(self):
        """Actualiza clipboard, historial, status."""
        clip = self._editor.get_clipboard()
        self._clip_label.config(text=clip if clip else "(vacío)")

        self._history_list.delete(0, "end")
        for i, cmd in enumerate(self._invoker.history):
            self._history_list.insert("end", f" {i + 1}. {cmd}")

        if self._invoker.redo_stack:
            self._history_list.insert("end", " ─── redo pendiente ───")
            for cmd in reversed(self._invoker.redo_stack):
                self._history_list.insert("end", f" ↪ {cmd}")

        # Auto-scroll al final
        self._history_list.see("end")
        self._update_status()

    def _update_status(self):
        content = self._text_widget.get("1.0", "end-1c")
        pos = self._cursor_pos()
        sel = self._selection_range()
        sel_text = f"Sel: [{sel[0]}:{sel[0]+sel[1]}] ({sel[1]} chars)" if sel else "Sel: ninguna"
        self._status.config(
            text=f"Pos: {pos}  |  {sel_text}  |  Chars: {len(content)}  |  "
                 f"Undo: {len(self._invoker.history)}  Redo: {len(self._invoker.redo_stack)}"
        )

    # ═══════════════════════════════════════════════════════════
    #  Handlers de eventos
    # ═══════════════════════════════════════════════════════════

    def _on_key(self, event):
        """Intercepta teclas de caracteres imprimibles para crear WriteCommands."""
        if self._syncing:
            return

        # Ignorar teclas de control/modificadores
        if event.state & 0x4:  # Ctrl
            return
        # Alt / AltGr — usar keysym (0x8 es NumLock en Windows, NO Alt)
        if event.keysym in ("Alt_L", "Alt_R", "ISO_Level3_Shift"):
            return
        if event.keysym.startswith("Alt"):
            return

        char = event.char
        if not char or len(char) != 1 or ord(char) < 32:
            # No es un carácter imprimible (flechas, F-keys, etc.)
            return

        # Si hay selección, primero borrar
        sel = self._selection_range()
        if sel:
            start, length = sel
            del_cmd = DeleteCommand(self._editor, start, length)
            self._invoker.execute_command(del_cmd)
            pos = start
        else:
            pos = self._cursor_pos()

        cmd = WriteCommand(self._editor, pos, char)
        self._invoker.execute_command(cmd)

        self._sync_widget_from_editor()
        # Mover cursor después del carácter insertado
        self._set_cursor_at(pos + 1)
        self._refresh_panels()
        self._log(f"✅ Write: '{char}' en pos {pos}")
        return "break"

    def _on_backspace(self, event):
        """Intercepta Backspace para crear DeleteCommand."""
        if self._syncing:
            return

        sel = self._selection_range()
        if sel:
            start, length = sel
        else:
            pos = self._cursor_pos()
            if pos == 0:
                return "break"
            start = pos - 1
            length = 1

        cmd = DeleteCommand(self._editor, start, length)
        self._invoker.execute_command(cmd)

        self._sync_widget_from_editor()
        self._set_cursor_at(start)
        self._refresh_panels()
        self._log(f"🗑️ Delete: {length} char(s) desde pos {start}")
        return "break"

    def _on_delete_key(self):
        """Tecla Delete — borra selección o carácter adelante."""
        sel = self._selection_range()
        if sel:
            start, length = sel
        else:
            pos = self._cursor_pos()
            content = self._editor.get_text()
            if pos >= len(content):
                return
            start = pos
            length = 1

        cmd = DeleteCommand(self._editor, start, length)
        self._invoker.execute_command(cmd)

        self._sync_widget_from_editor()
        self._set_cursor_at(start)
        self._refresh_panels()
        self._log(f"🗑️ Delete: {length} char(s) desde pos {start}")

    def _set_cursor_at(self, pos: int):
        """Posiciona el cursor del widget en un índice lineal."""
        content = self._text_widget.get("1.0", "end-1c")
        line = 1
        col = 0
        for i, ch in enumerate(content):
            if i == pos:
                break
            if ch == "\n":
                line += 1
                col = 0
            else:
                col += 1
        else:
            # pos == len(content)
            if pos == len(content):
                if content and content[-1] == "\n":
                    line += 1
                    col = 0
                # else: col ya está bien
        self._text_widget.mark_set("insert", f"{line}.{col}")
        self._text_widget.see("insert")

    # ── Botones de operaciones ──────────────────────────────────

    def _on_write(self):
        """Botón Write — escribe lo que está en el widget (sincronización completa)."""
        # Ya se escribe carácter a carácter con _on_key.
        # Este botón fuerza sincronización si el usuario pegó algo externamente.
        widget_text = self._text_widget.get("1.0", "end-1c")
        editor_text = self._editor.get_text()

        if widget_text != editor_text:
            # Reemplazar todo el contenido del editor con lo del widget
            if editor_text:
                del_cmd = DeleteCommand(self._editor, 0, len(editor_text))
                self._invoker.execute_command(del_cmd)
            if widget_text:
                write_cmd = WriteCommand(self._editor, 0, widget_text)
                self._invoker.execute_command(write_cmd)
            self._refresh_panels()
            self._log("✅ Write: contenido sincronizado")
        else:
            self._log("ℹ️ El editor ya está sincronizado")

    def _on_delete(self):
        """Botón Delete — borra la selección actual."""
        self._ensure_sync()
        sel = self._selection_range()
        if not sel:
            messagebox.showinfo("Delete", "Selecciona texto para borrar.")
            return
        start, length = sel
        cmd = DeleteCommand(self._editor, start, length)
        self._invoker.execute_command(cmd)
        self._sync_widget_from_editor()
        self._set_cursor_at(start)
        self._refresh_panels()
        self._log(f"🗑️ Delete: {length} chars desde pos {start}")

    def _on_copy(self):
        """Botón / Ctrl+C — copia la selección al clipboard."""
        self._ensure_sync()
        sel = self._selection_range()
        if not sel:
            self._log("⚠️ Selecciona texto para copiar")
            return
        start, length = sel
        cmd = CopyCommand(self._editor, start, length)
        self._invoker.execute_command(cmd)
        self._refresh_panels()
        self._log(f"📋 Copy: '{self._editor.get_clipboard()}'")

    def _on_cut(self):
        """Botón / Ctrl+X — corta la selección."""
        self._ensure_sync()
        sel = self._selection_range()
        if not sel:
            self._log("⚠️ Selecciona texto para cortar")
            return
        start, length = sel
        cmd = CutCommand(self._editor, start, length)
        self._invoker.execute_command(cmd)
        self._sync_widget_from_editor()
        self._set_cursor_at(start)
        self._refresh_panels()
        self._log(f"✂️ Cut: '{self._editor.get_clipboard()}'")

    def _on_paste(self):
        """Botón / Ctrl+V — pega el clipboard en la posición del cursor."""
        self._ensure_sync()
        clip = self._editor.get_clipboard()
        if not clip:
            self._log("⚠️ Clipboard vacío, nada que pegar")
            return

        sel = self._selection_range()
        if sel:
            start, length = sel
            del_cmd = DeleteCommand(self._editor, start, length)
            self._invoker.execute_command(del_cmd)
            pos = start
        else:
            pos = self._cursor_pos()

        cmd = PasteCommand(self._editor, pos)
        self._invoker.execute_command(cmd)
        self._sync_widget_from_editor()
        self._set_cursor_at(pos + len(clip))
        self._refresh_panels()
        self._log(f"📌 Paste: '{clip}' en pos {pos}")

    def _on_undo(self):
        """Botón / Ctrl+Z — deshace el último comando."""
        if self._invoker.undo_last_command():
            self._sync_widget_from_editor()
            self._refresh_panels()
            self._log("⬅️ Undo ejecutado")
        else:
            self._log("⚠️ No hay comandos para deshacer")

    def _on_redo(self):
        """Botón / Ctrl+Y — rehace el último comando deshecho."""
        if self._invoker.redo_last_command():
            self._sync_widget_from_editor()
            self._refresh_panels()
            self._log("➡️ Redo ejecutado")
        else:
            self._log("⚠️ No hay comandos para rehacer")

    # ═══════════════════════════════════════════════════════════
    #  Ejecución
    # ═══════════════════════════════════════════════════════════

    def run(self):
        self._text_widget.focus_set()
        self._root.mainloop()


# ═══════════════════════════════════════════════════════════════
#  Punto de entrada
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = Client()
    app.run()
