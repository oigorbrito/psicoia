package org.psicoia.android.core;

public final class ChatMessage {
    public String role;
    public String text;
    public long createdAtEpochMs;

    public ChatMessage() {}

    public ChatMessage(String role, String text, long createdAtEpochMs) {
        this.role = role;
        this.text = text;
        this.createdAtEpochMs = createdAtEpochMs;
    }
}
