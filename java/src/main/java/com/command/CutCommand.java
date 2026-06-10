package com.command;

/** Corta texto del editor y lo pone en el clipboard. */
public class CutCommand implements Command {

    private final TextEditor editor;
    private String cutText = "";   // - cutText: String
    private final int length;      // - length: int
    private final int start;       // - start: int

    public CutCommand(TextEditor editor, int start, int length) {
        this.editor = editor;
        this.start = start;
        this.length = length;
    }

    @Override
    public void execute() {
        this.cutText = editor.cut(start, length);
    }

    @Override
    public void undo() {
        editor.write(start, cutText);
    }

    @Override
    public void redo() {
        execute();
    }

    @Override
    public String toString() {
        return String.format("Cut(start=%d, len=%d, cut='%s')", start, length, cutText);
    }
}
