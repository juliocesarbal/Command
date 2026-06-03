"""
Patrón Command - Interfaz y Comandos Concretos
"""

from abc import ABC, abstractmethod
from text_editor import TextEditor


# ═══════════════════════════════════════════════════════════════
#  Interfaz Command
# ═══════════════════════════════════════════════════════════════

class Command(ABC):
    """Interfaz Command con execute, undo, redo."""

    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass

    @abstractmethod
    def redo(self) -> None:
        pass


# ═══════════════════════════════════════════════════════════════
#  Comandos Concretos
# ═══════════════════════════════════════════════════════════════

class WriteCommand(Command):
    """Escribe texto en una posición del editor."""

    def __init__(self, editor: TextEditor, position: int, text: str):
        self._editor = editor
        self._position = position
        self._text = text

    def execute(self) -> None:
        self._editor.write(self._position, self._text)

    def undo(self) -> None:
        self._editor.delete(self._position, len(self._text))

    def redo(self) -> None:
        self.execute()

    def __repr__(self) -> str:
        return f"Write(pos={self._position}, text='{self._text}')"


class DeleteCommand(Command):
    """Elimina texto desde una posición en el editor."""

    def __init__(self, editor: TextEditor, start: int, length: int):
        self._editor = editor
        self._start = start
        self._length = length
        self._deleted_text: str = ""

    def execute(self) -> None:
        self._deleted_text = self._editor.delete(self._start, self._length)

    def undo(self) -> None:
        self._editor.write(self._start, self._deleted_text)

    def redo(self) -> None:
        self.execute()

    def __repr__(self) -> str:
        return f"Delete(start={self._start}, len={self._length}, deleted='{self._deleted_text}')"


class CopyCommand(Command):
    """Copia texto al clipboard sin modificar el editor."""

    def __init__(self, editor: TextEditor, start: int, length: int):
        self._editor = editor
        self._start = start
        self._length = length

    def execute(self) -> None:
        self._editor.copy(self._start, self._length)

    def undo(self) -> None:
        # Copy no modifica el texto, nada que deshacer
        pass

    def redo(self) -> None:
        self.execute()

    def __repr__(self) -> str:
        return f"Copy(start={self._start}, len={self._length})"


class CutCommand(Command):
    """Corta texto del editor y lo pone en el clipboard."""

    def __init__(self, editor: TextEditor, start: int, length: int):
        self._editor = editor
        self._start = start
        self._length = length
        self._cut_text: str = ""

    def execute(self) -> None:
        self._cut_text = self._editor.cut(self._start, self._length)

    def undo(self) -> None:
        self._editor.write(self._start, self._cut_text)
        self._editor.set_clipboard(self._cut_text)

    def redo(self) -> None:
        self.execute()

    def __repr__(self) -> str:
        return f"Cut(start={self._start}, len={self._length}, cut='{self._cut_text}')"


class PasteCommand(Command):
    """Pega el contenido del clipboard en una posición."""

    def __init__(self, editor: TextEditor, position: int):
        self._editor = editor
        self._position = position
        self._pasted_text: str = ""

    def execute(self) -> None:
        self._pasted_text = self._editor.get_clipboard()
        self._editor.paste(self._position)

    def undo(self) -> None:
        if self._pasted_text:
            self._editor.delete(self._position, len(self._pasted_text))

    def redo(self) -> None:
        self.execute()

    def __repr__(self) -> str:
        return f"Paste(pos={self._position}, pasted='{self._pasted_text}')"
