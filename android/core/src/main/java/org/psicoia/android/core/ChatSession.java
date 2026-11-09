package org.psicoia.android.core;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public final class ChatSession {
    public String sessionId;
    public String sect;
    public int stage;
    public long createdAtEpochMs;
    public long updatedAtEpochMs;
    public List<ChatMessage> messages = new ArrayList<>();

    public ChatSession() {}

    public static ChatSession create(String sect, int stage) {
        long now = System.currentTimeMillis();
        ChatSession session = new ChatSession();
        session.sessionId = UUID.randomUUID().toString();
        session.sect = sect;
        session.stage = stage;
        session.createdAtEpochMs = now;
        session.updatedAtEpochMs = now;
        return session;
    }
}
