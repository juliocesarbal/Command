"""
Patrón Command - Interfaz y Comandos Concretos
Nombres exactos del diagrama UML.
"""

from abc import ABC, abstractmethod
from text_editor import TextEditor


# ═══════════════════════════════════════════════════════════════
#  «interface» Command
# ═══════════════════════════════════════════════════════════════

class Command(ABC):
    """«interface» Command: execute, undo, redo."""

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
        self.editor = editor
        self.position: int = position     # - position: int
        self.text: str = text             # - text: int  (str en Python)

    def execute(self) -> None:
        self.editor.write(self.position, self.text)

    def undo(self) -> None:
        self.editor.delete(self.position, len(self.text))

    def redo(self) -> None:
        self.execute()

    def __repr__(self) -> str:
        return f"Write(pos={self.position}, text='{self.text}')"


class DeleteCommand(Command):
    """Elimina texto desde una posición en el editor."""

    def __init__(self, editor: TextEditor, start: int, length: int):
        self.editor = editor
        self.deletedText: str = ""        # - deletedText: String
        self.length: int = length         # - length: int
        self.start: int = start           # - start: int

    def execute(self) -> None:
        self.deletedText = self.editor.delete(self.start, self.length)

    def undo(self) -> None:
        self.editor.write(self.start, self.deletedText)

    def redo(self) -> None:
        self.execute()

    def __repr__(self) -> str:
        return f"Delete(start={self.start}, len={self.length}, deleted='{self.deletedText}')"


class CopyCommand(Command):
    """Copia texto al clipboard sin modificar el editor."""

    def __init__(self, editor: TextEditor, start: int, length: int):
        self.editor = editor
        self.length: int = length         # - length: int
        self.start: int = start           # - start: int

    def execute(self) -> None:
        self.editor.copy(self.start, self.length)

    def undo(self) -> None:
        # Copy no modifica el texto, nada que deshacer
        pass

    def redo(self) -> None:
        self.execute()

    def __repr__(self) -> str:
        return f"Copy(start={self.start}, len={self.length})"


class CutCommand(Command):
    """Corta texto del editor y lo pone en el clipboard."""

    def __init__(self, editor: TextEditor, start: int, length: int):
        self.editor = editor
        self.cutText: str = ""            # - cutText: String
        self.length: int = length         # - length: int
        self.start: int = start           # - start: int

    def execute(self) -> None:
        self.cutText = self.editor.cut(self.start, self.length)

    def undo(self) -> None:
        self.editor.write(self.start, self.cutText)

    def redo(self) -> None:
        self.execute()

    def __repr__(self) -> str:
        return f"Cut(start={self.start}, len={self.length}, cut='{self.cutText}')"


class PasteCommand(Command):
    """Pega el contenido del clipboard en una posición."""

    def __init__(self, editor: TextEditor, position: int):
        self.editor = editor
        self.position: int = position     # - position: int
        self._pastedLen: int = 0          # auxiliar para undo

    def execute(self) -> None:
        self._pastedLen = len(self.editor.getClipboard())
        self.editor.paste(self.position)

    def undo(self) -> None:
        if self._pastedLen > 0:
            self.editor.delete(self.position, self._pastedLen)

    def redo(self) -> None:
        self.execute()

    def __repr__(self) -> str:
        return f"Paste(pos={self.position})"
