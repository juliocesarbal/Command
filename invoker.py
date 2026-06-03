"""
Patrón Command - Invoker
TextEditorInvoker: executeCommand, redoLastCommand, undoLastCommand
"""

from commands import Command


class TextEditorInvoker:
    """Invoker - Ejecuta comandos y gestiona historial de undo/redo."""

    def __init__(self):
        self._history: list[Command] = []
        self._redoStack: list[Command] = []

    def executeCommand(self, command: Command) -> None:
        """Ejecuta un comando y lo agrega al historial."""
        command.execute()
        self._history.append(command)
        self._redoStack.clear()

    def undoLastCommand(self) -> bool:
        """Deshace el último comando. Retorna True si se pudo deshacer."""
        if not self._history:
            return False
        command = self._history.pop()
        command.undo()
        self._redoStack.append(command)
        return True

    def redoLastCommand(self) -> bool:
        """Rehace el último comando deshecho. Retorna True si se pudo rehacer."""
        if not self._redoStack:
            return False
        command = self._redoStack.pop()
        command.redo()
        self._history.append(command)
        return True

    @property
    def history(self) -> list[Command]:
        return list(self._history)

    @property
    def redoStack(self) -> list[Command]:
        return list(self._redoStack)
