package com.command;

/**
 * «interface» Command: execute, undo, redo.
 */
public interface Command {
    void execute();
    void undo();
    void redo();
}
