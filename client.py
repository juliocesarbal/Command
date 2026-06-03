"""
Patrón Command — Cliente (Interfaz Gráfica con Tkinter)
Client: copy, cut, delete, paste, write  — tal cual el diagrama UML.
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
    """Client — copy(), cut(), delete(), paste(), write()."""

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
        self._syncing = False

        self._root = tk.Tk()
        self._root.title("Patrón Command — Editor de Texto")
        self._root.geometry("900x640")
        self._root.configure(bg=self.BG)
        self._root.minsize(750, 550)

        self._setupStyles()
        self._buildUI()
        self._bindShortcuts()

    # ═══════════════════════════════════════════════════════════
    #  Estilos
    # ═══════════════════════════════════════════════════════════

    def _setupStyles(self):
        s = ttk.Style()
        s.theme_use("clam")

        s.configure("Title.TLabel",
                     font=("Segoe UI", 15, "bold"),
                     foreground=self.TEXT_CLR, background=self.BG)
        s.configure("Sub.TLabel",
                     font=("Segoe UI", 9),
                     foreground=self.SUBTEXT, background=self.BG)
        s.configure("Section.TLabelframe", background=self.BG)
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
    #  UI
    # ═══════════════════════════════════════════════════════════

    def _buildUI(self):
        # Header
        header = tk.Frame(self._root, bg=self.BG)
        header.pack(fill="x", padx=20, pady=(14, 4))
        ttk.Label(header, text="✏️  Editor de Texto — Patrón Command",
                  style="Title.TLabel").pack(side="left")
        ttk.Label(header,
                  text="Escribe · Selecciona · Usa botones o atajos",
                  style="Sub.TLabel").pack(side="left", padx=(16, 0))

        # Toolbar
        toolbar = tk.Frame(self._root, bg=self.SURFACE, pady=6)
        toolbar.pack(fill="x", padx=20, pady=(6, 0))

        for text, style, cmd in [
            ("📝 Write",        "Write.TButton",  self.write),
            ("🗑️ Delete (Del)", "Delete.TButton", self.delete),
            ("📋 Copy (Ctrl+C)", "Copy.TButton",  self.copy),
            ("✂️ Cut (Ctrl+X)", "Cut.TButton",    self.cut),
            ("📌 Paste (Ctrl+V)", "Paste.TButton", self.paste),
        ]:
            ttk.Button(toolbar, text=text, style=style,
                       command=cmd).pack(side="left", padx=4)

        tk.Frame(toolbar, width=2, bg=self.OVERLAY).pack(
            side="left", fill="y", padx=8, pady=2)

        ttk.Button(toolbar, text="⬅️ Undo (Ctrl+Z)", style="Undo.TButton",
                   command=self._onUndo).pack(side="left", padx=4)
        ttk.Button(toolbar, text="➡️ Redo (Ctrl+Y)", style="Redo.TButton",
                   command=self._onRedo).pack(side="left", padx=4)

        # Body
        body = tk.PanedWindow(self._root, orient="horizontal",
                              bg=self.OVERLAY, sashwidth=4)
        body.pack(fill="both", expand=True, padx=20, pady=10)

        # Editor area
        textFrame = ttk.LabelFrame(body, text=" Editor ",
                                   style="Section.TLabelframe")
        body.add(textFrame, width=520)

        self._textWidget = tk.Text(
            textFrame, font=("Consolas", 13), wrap="word",
            bg=self.SURFACE, fg=self.TEXT_CLR, insertbackground=self.TEAL,
            selectbackground=self.BLUE, selectforeground=self.BG,
            relief="flat", padx=12, pady=10, undo=False,
        )
        self._textWidget.pack(fill="both", expand=True, padx=8, pady=8)

        # Right panel
        right = tk.Frame(body, bg=self.BG)
        body.add(right, width=320)

        # Clipboard
        clipFrame = ttk.LabelFrame(right, text=" 📋 Clipboard ",
                                   style="Section.TLabelframe")
        clipFrame.pack(fill="x", padx=4, pady=(4, 6))
        self._clipLabel = tk.Label(
            clipFrame, text="(vacío)", font=("Consolas", 10),
            fg=self.PINK, bg=self.SURFACE, anchor="w",
            padx=8, pady=6, wraplength=260, justify="left",
        )
        self._clipLabel.pack(fill="x", padx=8, pady=6)

        # History
        histFrame = ttk.LabelFrame(right, text=" 📜 Historial de Comandos ",
                                   style="Section.TLabelframe")
        histFrame.pack(fill="both", expand=True, padx=4, pady=(0, 6))
        histScroll = tk.Scrollbar(histFrame)
        histScroll.pack(side="right", fill="y", pady=6, padx=(0, 6))
        self._historyList = tk.Listbox(
            histFrame, font=("Consolas", 9),
            bg=self.SURFACE, fg=self.GREEN,
            selectbackground=self.OVERLAY, relief="flat",
            yscrollcommand=histScroll.set,
        )
        self._historyList.pack(fill="both", expand=True, padx=(8, 0), pady=6)
        histScroll.config(command=self._historyList.yview)

        # Log
        logFrame = ttk.LabelFrame(right, text=" 💬 Log ",
                                  style="Section.TLabelframe")
        logFrame.pack(fill="x", padx=4, pady=(0, 4))
        self._logLabel = tk.Label(
            logFrame, text="Listo. Escribe algo en el editor.",
            font=("Segoe UI", 9), fg=self.TEAL, bg=self.SURFACE,
            anchor="w", padx=8, pady=5, wraplength=280, justify="left",
        )
        self._logLabel.pack(fill="x", padx=8, pady=6)

        # Status bar
        self._status = tk.Label(
            self._root, text="Pos: 0  |  Sel: ninguna  |  Chars: 0",
            font=("Segoe UI", 8), fg=self.SUBTEXT, bg=self.OVERLAY,
            anchor="w", padx=12, pady=3,
        )
        self._status.pack(fill="x", side="bottom")

    # ═══════════════════════════════════════════════════════════
    #  Shortcuts
    # ═══════════════════════════════════════════════════════════

    def _bindShortcuts(self):
        w = self._textWidget
        w.bind("<Key>", self._onKey)
        w.bind("<BackSpace>", self._onBackspace)
        w.bind("<Control-c>", lambda e: (self.copy(), "break")[1])
        w.bind("<Control-x>", lambda e: (self.cut(), "break")[1])
        w.bind("<Control-v>", lambda e: (self.paste(), "break")[1])
        w.bind("<Control-z>", lambda e: (self._onUndo(), "break")[1])
        w.bind("<Control-y>", lambda e: (self._onRedo(), "break")[1])
        w.bind("<Delete>",    lambda e: (self._onDeleteKey(), "break")[1])
        w.bind("<ButtonRelease-1>", lambda e: self._updateStatus())
        w.bind("<KeyRelease>", lambda e: self._updateStatus())

    # ═══════════════════════════════════════════════════════════
    #  Helpers
    # ═══════════════════════════════════════════════════════════

    def _cursorPos(self) -> int:
        idx = self._textWidget.index("insert")
        line, col = map(int, idx.split("."))
        content = self._textWidget.get("1.0", "end-1c")
        lines = content.split("\n")
        return sum(len(lines[i]) + 1 for i in range(line - 1)) + col

    def _selectionRange(self):
        try:
            selStart = self._textWidget.index("sel.first")
            selEnd = self._textWidget.index("sel.last")
            content = self._textWidget.get("1.0", "end-1c")

            def idxToInt(idxStr):
                line, col = map(int, idxStr.split("."))
                lines = content.split("\n")
                return sum(len(lines[i]) + 1 for i in range(line - 1)) + col

            start = idxToInt(selStart)
            end = idxToInt(selEnd)
            return start, end - start
        except tk.TclError:
            return None

    def _log(self, msg: str):
        self._logLabel.config(text=msg)

    def _ensureSync(self):
        """Sincroniza el TextEditor desde el widget si están desfasados."""
        widgetText = self._textWidget.get("1.0", "end-1c")
        editorText = self._editor.getText()
        if widgetText != editorText:
            if editorText:
                delCmd = DeleteCommand(self._editor, 0, len(editorText))
                self._invoker.executeCommand(delCmd)
            if widgetText:
                writeCmd = WriteCommand(self._editor, 0, widgetText)
                self._invoker.executeCommand(writeCmd)

    def _syncWidgetFromEditor(self):
        self._syncing = True
        cursor = self._textWidget.index("insert")
        self._textWidget.delete("1.0", "end")
        self._textWidget.insert("1.0", self._editor.getText())
        try:
            self._textWidget.mark_set("insert", cursor)
        except tk.TclError:
            self._textWidget.mark_set("insert", "end")
        self._syncing = False

    def _refreshPanels(self):
        clip = self._editor.getClipboard()
        self._clipLabel.config(text=clip if clip else "(vacío)")

        self._historyList.delete(0, "end")
        for i, cmd in enumerate(self._invoker.history):
            self._historyList.insert("end", f" {i + 1}. {cmd}")

        if self._invoker.redoStack:
            self._historyList.insert("end", " ─── redo pendiente ───")
            for cmd in reversed(self._invoker.redoStack):
                self._historyList.insert("end", f" ↪ {cmd}")

        self._historyList.see("end")
        self._updateStatus()

    def _updateStatus(self):
        content = self._textWidget.get("1.0", "end-1c")
        pos = self._cursorPos()
        sel = self._selectionRange()
        selText = f"Sel: [{sel[0]}:{sel[0]+sel[1]}] ({sel[1]} chars)" if sel else "Sel: ninguna"
        self._status.config(
            text=f"Pos: {pos}  |  {selText}  |  Chars: {len(content)}  |  "
                 f"Undo: {len(self._invoker.history)}  Redo: {len(self._invoker.redoStack)}"
        )

    def _setCursorAt(self, pos: int):
        content = self._textWidget.get("1.0", "end-1c")
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
            if pos == len(content):
                if content and content[-1] == "\n":
                    line += 1
                    col = 0
        self._textWidget.mark_set("insert", f"{line}.{col}")
        self._textWidget.see("insert")

    # ═══════════════════════════════════════════════════════════
    #  Handlers de teclas
    # ═══════════════════════════════════════════════════════════

    def _onKey(self, event):
        if self._syncing:
            return
        if event.state & 0x4:  # Ctrl
            return
        if event.keysym in ("Alt_L", "Alt_R", "ISO_Level3_Shift"):
            return
        if event.keysym.startswith("Alt"):
            return

        char = event.char
        if not char or len(char) != 1 or ord(char) < 32:
            return

        sel = self._selectionRange()
        if sel:
            start, length = sel
            delCmd = DeleteCommand(self._editor, start, length)
            self._invoker.executeCommand(delCmd)
            pos = start
        else:
            pos = self._cursorPos()

        cmd = WriteCommand(self._editor, pos, char)
        self._invoker.executeCommand(cmd)
        self._syncWidgetFromEditor()
        self._setCursorAt(pos + 1)
        self._refreshPanels()
        self._log(f"✅ Write: '{char}' en pos {pos}")
        return "break"

    def _onBackspace(self, event):
        if self._syncing:
            return
        self._ensureSync()

        sel = self._selectionRange()
        if sel:
            start, length = sel
        else:
            pos = self._cursorPos()
            if pos == 0:
                return "break"
            start = pos - 1
            length = 1

        cmd = DeleteCommand(self._editor, start, length)
        self._invoker.executeCommand(cmd)
        self._syncWidgetFromEditor()
        self._setCursorAt(start)
        self._refreshPanels()
        self._log(f"🗑️ Delete: {length} char(s) desde pos {start}")
        return "break"

    def _onDeleteKey(self):
        self._ensureSync()
        sel = self._selectionRange()
        if sel:
            start, length = sel
        else:
            pos = self._cursorPos()
            content = self._editor.getText()
            if pos >= len(content):
                return
            start = pos
            length = 1

        cmd = DeleteCommand(self._editor, start, length)
        self._invoker.executeCommand(cmd)
        self._syncWidgetFromEditor()
        self._setCursorAt(start)
        self._refreshPanels()
        self._log(f"🗑️ Delete: {length} char(s) desde pos {start}")

    # ═══════════════════════════════════════════════════════════
    #  Métodos públicos del Client (tal cual el diagrama)
    #  + copy(): void
    #  + cut(): void
    #  + delete(): void
    #  + paste(): void
    #  + write(): void
    # ═══════════════════════════════════════════════════════════

    def write(self):
        """+ write(): void — Sincroniza el widget con el editor."""
        self._ensureSync()
        self._refreshPanels()
        self._log("✅ Write: contenido sincronizado")

    def delete(self):
        """+ delete(): void — Borra la selección actual."""
        self._ensureSync()
        sel = self._selectionRange()
        if not sel:
            messagebox.showinfo("Delete", "Selecciona texto para borrar.")
            return
        start, length = sel
        cmd = DeleteCommand(self._editor, start, length)
        self._invoker.executeCommand(cmd)
        self._syncWidgetFromEditor()
        self._setCursorAt(start)
        self._refreshPanels()
        self._log(f"🗑️ Delete: {length} chars desde pos {start}")

    def copy(self):
        """+ copy(): void — Copia la selección al clipboard."""
        self._ensureSync()
        sel = self._selectionRange()
        if not sel:
            self._log("⚠️ Selecciona texto para copiar")
            return
        start, length = sel
        cmd = CopyCommand(self._editor, start, length)
        self._invoker.executeCommand(cmd)
        self._refreshPanels()
        self._log(f"📋 Copy: '{self._editor.getClipboard()}'")

    def cut(self):
        """+ cut(): void — Corta la selección."""
        self._ensureSync()
        sel = self._selectionRange()
        if not sel:
            self._log("⚠️ Selecciona texto para cortar")
            return
        start, length = sel
        cmd = CutCommand(self._editor, start, length)
        self._invoker.executeCommand(cmd)
        self._syncWidgetFromEditor()
        self._setCursorAt(start)
        self._refreshPanels()
        self._log(f"✂️ Cut: '{self._editor.getClipboard()}'")

    def paste(self):
        """+ paste(): void — Pega el clipboard en la posición del cursor."""
        self._ensureSync()
        clip = self._editor.getClipboard()
        if not clip:
            self._log("⚠️ Clipboard vacío, nada que pegar")
            return

        sel = self._selectionRange()
        if sel:
            start, length = sel
            delCmd = DeleteCommand(self._editor, start, length)
            self._invoker.executeCommand(delCmd)
            pos = start
        else:
            pos = self._cursorPos()

        cmd = PasteCommand(self._editor, pos)
        self._invoker.executeCommand(cmd)
        self._syncWidgetFromEditor()
        self._setCursorAt(pos + len(clip))
        self._refreshPanels()
        self._log(f"📌 Paste: '{clip}' en pos {pos}")

    def _onUndo(self):
        if self._invoker.undoLastCommand():
            self._syncWidgetFromEditor()
            self._refreshPanels()
            self._log("⬅️ Undo ejecutado")
        else:
            self._log("⚠️ No hay comandos para deshacer")

    def _onRedo(self):
        if self._invoker.redoLastCommand():
            self._syncWidgetFromEditor()
            self._refreshPanels()
            self._log("➡️ Redo ejecutado")
        else:
            self._log("⚠️ No hay comandos para rehacer")

    # ═══════════════════════════════════════════════════════════
    #  Ejecución
    # ═══════════════════════════════════════════════════════════

    def run(self):
        self._textWidget.focus_set()
        self._root.mainloop()


if __name__ == "__main__":
    app = Client()
    app.run()
