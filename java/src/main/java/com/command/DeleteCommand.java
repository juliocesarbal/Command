package com.command;

/** Elimina texto desde una posición en el editor. */
public class DeleteCommand implements Command {

    private final TextEditor editor;
    private String deletedText = "";   // - deletedText: String
    private final int length;          // - length: int
    private final int start;           // - start: int

    public DeleteCommand(TextEditor editor, int start, int length) {
        this.editor = editor;
        this.start = start;
        this.length = length;
    }

    @Override
    public void execute() {
        this.deletedText = editor.delete(start, length);
    }

    @Override
    public void undo() {
        editor.write(start, deletedText);
    }

    @Override
    public void redo() {
        execute();
    }

    @Override
    public String toString() {
        return String.format("Delete(start=%d, len=%d, deleted='%s')", start, length, deletedText);
    }
}
