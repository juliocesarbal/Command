package com.command;

/** Copia texto al clipboard sin modificar el editor. */
public class CopyCommand implements Command {

    private final TextEditor editor;
    private final int length;   // - length: int
    private final int start;    // - start: int

    public CopyCommand(TextEditor editor, int start, int length) {
        this.editor = editor;
        this.start = start;
        this.length = length;
    }

    @Override
    public void execute() {
        editor.copy(start, length);
    }

    @Override
    public void undo() {
        // Copy no modifica el texto, nada que deshacer
    }

    @Override
    public void redo() {
        execute();
    }

    @Override
    public String toString() {
        return String.format("Copy(start=%d, len=%d)", start, length);
    }
}
