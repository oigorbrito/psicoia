package org.psicoia.android.core;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.regex.Pattern;

/** JSON conversation persistence under the app-private files directory. */
public final class ConversationStore {
    private static final Pattern SAFE_ID = Pattern.compile("[0-9a-fA-F-]{36}");
    private final File sessionsDirectory;
    private final Gson gson = new GsonBuilder().disableHtmlEscaping().create();

    public ConversationStore(File appFilesDirectory) {
        this.sessionsDirectory = new File(appFilesDirectory, "conversations");
    }

    public synchronized ChatSession create(String sect, int stage) throws IOException {
        if (sect == null || sect.isBlank() || stage < 1 || stage > 3) {
            throw new IllegalArgumentException("A supported approach and stage 1..3 are required");
        }
        ChatSession session = ChatSession.create(sect, stage);
        save(session);
        return session;
    }

    public synchronized ChatSession load(String sessionId) throws IOException {
        File file = sessionFile(sessionId);
        if (!file.isFile()) throw new IOException("Conversation does not exist: " + sessionId);
        try {
            ChatSession session = gson.fromJson(Files.readString(file.toPath(), StandardCharsets.UTF_8), ChatSession.class);
            if (session == null || !sessionId.equals(session.sessionId) || session.messages == null) {
                throw new IOException("Conversation file is invalid: " + sessionId);
            }
            return session;
        } catch (RuntimeException e) {
            throw new IOException("Conversation file is invalid: " + sessionId, e);
        }
    }

    public synchronized void append(String sessionId, String role, String text) throws IOException {
        if (!("user".equals(role) || "assistant".equals(role) || "error".equals(role))) {
            throw new IllegalArgumentException("Unsupported message role: " + role);
        }
        if (text == null || text.isBlank()) throw new IllegalArgumentException("Message text is required");
        ChatSession session = load(sessionId);
        session.messages.add(new ChatMessage(role, text, System.currentTimeMillis()));
        session.updatedAtEpochMs = System.currentTimeMillis();
        save(session);
    }

    public synchronized void updateContext(String sessionId, String sect, int stage) throws IOException {
        if (sect == null || sect.isBlank() || stage < 1 || stage > 3) {
            throw new IllegalArgumentException("A supported approach and stage 1..3 are required");
        }
        ChatSession session = load(sessionId);
        session.sect = sect;
        session.stage = stage;
        session.updatedAtEpochMs = System.currentTimeMillis();
        save(session);
    }

    public synchronized List<ChatSession> list() throws IOException {
        if (!sessionsDirectory.exists()) return List.of();
        File[] files = sessionsDirectory.listFiles((dir, name) -> name.endsWith(".json"));
        if (files == null) throw new IOException("Cannot read conversation directory");
        List<ChatSession> sessions = new ArrayList<>();
        for (File file : files) sessions.add(load(file.getName().substring(0, file.getName().length() - 5)));
        sessions.sort(Comparator.comparingLong((ChatSession session) -> session.updatedAtEpochMs).reversed());
        return sessions;
    }

    private void save(ChatSession session) throws IOException {
        if (session == null || session.sessionId == null || session.messages == null) {
            throw new IllegalArgumentException("Invalid conversation");
        }
        File target = sessionFile(session.sessionId);
        if (!sessionsDirectory.exists() && !sessionsDirectory.mkdirs()) {
            throw new IOException("Cannot create app-private conversation directory");
        }
        File temporary = new File(sessionsDirectory, session.sessionId + ".tmp");
        byte[] bytes = gson.toJson(session).getBytes(StandardCharsets.UTF_8);
        try (FileOutputStream output = new FileOutputStream(temporary)) {
            output.write(bytes);
            output.getFD().sync();
        }
        try {
            Files.move(temporary.toPath(), target.toPath(), StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
        } catch (AtomicMoveNotSupportedException e) {
            Files.move(temporary.toPath(), target.toPath(), StandardCopyOption.REPLACE_EXISTING);
        }
    }

    private File sessionFile(String sessionId) {
        if (sessionId == null || !SAFE_ID.matcher(sessionId).matches()) {
            throw new IllegalArgumentException("Invalid conversation ID");
        }
        return new File(sessionsDirectory, sessionId + ".json");
    }
}
