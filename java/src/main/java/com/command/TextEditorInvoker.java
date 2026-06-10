package com.command;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

/**
 * Patrón Command - Invoker
 * TextEditorInvoker: executeCommand, redoLastCommand, undoLastCommand
 */
public class TextEditorInvoker {

    private final List<Command> history = new ArrayList<>();
    private final Deque<Command> redoStack = new ArrayDeque<>();

    /** Ejecuta un comando y lo agrega al historial. */
    public void executeCommand(Command command) {
        command.execute();
        history.add(command);
        redoStack.clear();
    }

    /** Deshace el último comando. Retorna true si se pudo deshacer. */
    public boolean undoLastCommand() {
        if (history.isEmpty()) {
            return false;
        }
        Command command = history.remove(history.size() - 1);
        command.undo();
        redoStack.push(command);
        return true;
    }

    /** Rehace el último comando deshecho. Retorna true si se pudo rehacer. */
    public boolean redoLastCommand() {
        if (redoStack.isEmpty()) {
            return false;
        }
        Command command = redoStack.pop();
        command.redo();
        history.add(command);
        return true;
    }

    // ── Accessors para panel de UI ──────────────────────────────

    public List<Command> getHistory() {
        return history;
    }

    public Deque<Command> getRedoStack() {
        return redoStack;
    }
}
