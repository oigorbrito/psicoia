package org.psicoia.android.core;

import static org.junit.Assert.*;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.junit.BeforeClass;
import org.junit.Test;

public class OfflineChatCoreTest {
    private static Path repoRoot;
    private static Map<String, String> sourceCatalogs;
    private static CatalogIndex index;

    @BeforeClass
    public static void loadSourceCatalogs() throws IOException {
        repoRoot = Path.of(System.getProperty("psicoia.repoRoot"));
        Path source = repoRoot.resolve("assets/skills/sect");
        sourceCatalogs = new LinkedHashMap<>();
        try (var paths = Files.walk(source)) {
            for (Path path : paths.filter(p -> p.toString().endsWith(".pt-BR.json")).sorted().toList()) {
                String relative = source.relativize(path).toString().replace('\\', '/');
                sourceCatalogs.put("sect/" + relative, Files.readString(path, StandardCharsets.UTF_8));
            }
        }
        index = CatalogIndex.fromJsonFiles(sourceCatalogs);
    }

    @Test
    public void catalogBundleIsByteIdenticalAndRetainsAllIdsAndHierarchy() throws IOException {
        Path source = repoRoot.resolve("assets/skills/sect");
        Path bundled = repoRoot.resolve("android/app/src/main/assets/catalog/sect");
        int records = 0;
        int files = 0;
        Gson gson = new Gson();
        for (Map.Entry<String, String> entry : sourceCatalogs.entrySet()) {
            Path sourceFile = source.resolve(entry.getKey().substring("sect/".length()));
            Path bundleFile = bundled.resolve(entry.getKey().substring("sect/".length()));
            assertArrayEquals("catalog bytes changed: " + entry.getKey(),
                    Files.readAllBytes(sourceFile), Files.readAllBytes(bundleFile));
            Map<String, SkillRecord> sourceRecords = gson.fromJson(entry.getValue(),
                    new TypeToken<Map<String, SkillRecord>>() {}.getType());
            Map<String, SkillRecord> bundledRecords = gson.fromJson(
                    Files.readString(bundleFile, StandardCharsets.UTF_8),
                    new TypeToken<Map<String, SkillRecord>>() {}.getType());
            assertEquals(sourceRecords.keySet(), bundledRecords.keySet());
            for (String id : sourceRecords.keySet()) {
                assertEquals(id, sourceRecords.get(id).skillId);
                assertEquals(sourceRecords.get(id).parentIds, bundledRecords.get(id).parentIds);
                records++;
            }
            files++;
        }
        assertEquals(30, files);
        assertEquals(CatalogIndex.EXPECTED_SOURCE_RECORDS, records);
        assertEquals(5158, index.getSourceRecordCount());
        assertEquals(4481, index.getMicroRecordCount());
        assertEquals(677, index.getMetaRecordCount());
    }

    @Test
    public void bm25RetrievalReturnsPtBrSkillAndRespectsApproachAndStage() {
        List<RetrievedSkill> hits = index.search("expressar compreensão e empatia", "cbt", 1, 5);
        assertFalse(hits.isEmpty());
        assertEquals("32", hits.get(0).record.skillId);
        assertEquals("Expressar compreensão e empatia", hits.get(0).record.skillName);
        assertEquals("micro", hits.get(0).catalogType);
        assertTrue(hits.get(0).record.parentIds.contains("3"));
        assertFalse(index.search("empatia", "pdt", 3, 5).stream()
                .anyMatch(hit -> hit.sect.equals("cbt") || hit.stage != 3));
        assertTrue(index.search(" ", "cbt", 1, 5).isEmpty());
    }

    @Test
    public void chatRetrievalAndConversationSurviveStoreReopen() throws IOException {
        Path appFiles = Files.createTempDirectory("psicoia-android-store");
        ConversationStore store = new ConversationStore(appFiles.toFile());
        ChatSession session = store.create("cbt", 1);
        ChatCoordinator coordinator = new ChatCoordinator(index, store);
        final String[] receivedPrompt = {null};
        ChatCoordinator.SendResult result = coordinator.send(session.sessionId, "Quero falar sobre empatia", prompt -> {
            receivedPrompt[0] = prompt;
            return "Podemos explorar o que isso significa para você.";
        });
        assertTrue(result.success);
        assertFalse(result.retrievedSkills.isEmpty());
        assertTrue(receivedPrompt[0].contains("Contexto local do catálogo PsicoIA"));
        assertTrue(receivedPrompt[0].contains("skill_id="));

        ChatSession restored = new ConversationStore(appFiles.toFile()).load(session.sessionId);
        assertEquals(2, restored.messages.size());
        assertEquals("user", restored.messages.get(0).role);
        assertEquals("assistant", restored.messages.get(1).role);
        assertEquals("Podemos explorar o que isso significa para você.", restored.messages.get(1).text);
    }

    @Test
    public void modelFailureIsVisibleAndPersistedWithoutFakeAssistantReply() throws IOException {
        Path appFiles = Files.createTempDirectory("psicoia-android-failure");
        ConversationStore store = new ConversationStore(appFiles.toFile());
        ChatSession session = store.create("cbt", 1);
        ChatCoordinator.SendResult result = new ChatCoordinator(index, store).send(
                session.sessionId, "Uma mensagem", prompt -> { throw new IOException("test failure"); });
        assertFalse(result.success);
        assertTrue(result.text.contains("geração local falhou"));
        ChatSession restored = store.load(session.sessionId);
        assertEquals(2, restored.messages.size());
        assertEquals("user", restored.messages.get(0).role);
        assertEquals("error", restored.messages.get(1).role);
        assertTrue(restored.messages.get(1).text.contains("geração local falhou"));
    }

    @Test(expected = IllegalArgumentException.class)
    public void conversationStoreRejectsPathTraversalIds() throws IOException {
        new ConversationStore(Files.createTempDirectory("psicoia-android-path").toFile()).load("../../escape");
    }
}
