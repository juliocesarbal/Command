"""
Patrón Command - Invoker
Gestiona el historial de comandos para undo/redo.
"""

from commands import Command


class TextEditorInvoker:
    """Invoker - Ejecuta comandos y gestiona historial de undo/redo."""

    def __init__(self):
        self._history: list[Command] = []
        self._redo_stack: list[Command] = []

    def execute_command(self, command: Command) -> None:
        """Ejecuta un comando y lo agrega al historial."""
        command.execute()
        self._history.append(command)
        self._redo_stack.clear()  # Al ejecutar un nuevo comando, se limpia el redo

    def undo_last_command(self) -> bool:
        """Deshace el último comando. Retorna True si se pudo deshacer."""
        if not self._history:
            return False
        command = self._history.pop()
        command.undo()
        self._redo_stack.append(command)
        return True

    def redo_last_command(self) -> bool:
        """Rehace el último comando deshecho. Retorna True si se pudo rehacer."""
        if not self._redo_stack:
            return False
        command = self._redo_stack.pop()
        command.redo()
        self._history.append(command)
        return True

    @property
    def history(self) -> list[Command]:
        return list(self._history)

    @property
    def redo_stack(self) -> list[Command]:
        return list(self._redo_stack)
