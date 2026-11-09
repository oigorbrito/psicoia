package org.psicoia.android.core;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/** Retrieves PT-BR skills, augments one local turn, and persists both successful and failed turns. */
public final class ChatCoordinator {
    private final CatalogIndex catalog;
    private final ConversationStore conversations;

    public ChatCoordinator(CatalogIndex catalog, ConversationStore conversations) {
        this.catalog = catalog;
        this.conversations = conversations;
    }

    public synchronized SendResult send(String sessionId, String userText, LocalChatEngine engine) {
        if (userText == null || userText.isBlank()) return SendResult.failure("Digite uma mensagem.", List.of());
        if (engine == null) return SendResult.failure("Carregue um modelo GGUF local antes de conversar.", List.of());

        final ChatSession session;
        try {
            session = conversations.load(sessionId);
            conversations.append(sessionId, "user", userText.trim());
        } catch (IOException | IllegalArgumentException e) {
            return SendResult.failure("Não foi possível salvar a mensagem localmente.", List.of());
        }

        List<RetrievedSkill> retrieved = catalog.search(userText, session.sect, session.stage, 5);
        String prompt = buildPrompt(userText.trim(), retrieved);
        try {
            String answer = engine.generate(prompt);
            if (answer == null || answer.isBlank()) throw new IOException("Modelo local retornou uma resposta vazia");
            conversations.append(sessionId, "assistant", answer.trim());
            return SendResult.success(answer.trim(), retrieved);
        } catch (Exception e) {
            String error = "A geração local falhou. A mensagem foi salva; verifique o modelo e tente novamente.";
            try {
                conversations.append(sessionId, "error", error);
            } catch (IOException ignored) {
                error = "A geração local falhou e o erro não pôde ser persistido.";
            }
            return SendResult.failure(error, retrieved);
        }
    }

    private static String buildPrompt(String query, List<RetrievedSkill> retrieved) {
        StringBuilder prompt = new StringBuilder();
        prompt.append("Mensagem da pessoa (PT-BR):\n").append(query);
        prompt.append("\n\nContexto local do catálogo PsicoIA (dados de pesquisa; não cite IDs ao usuário):");
        if (retrieved.isEmpty()) {
            prompt.append("\nNenhuma habilidade relevante foi recuperada.");
        } else {
            for (RetrievedSkill hit : retrieved) {
                SkillRecord record = hit.record;
                prompt.append("\n\n[sect=").append(hit.sect)
                        .append(" stage=").append(hit.stage)
                        .append(" skill_id=").append(record.skillId)
                        .append(" parent_ids=").append(String.join(",", record.parentIds)).append(']');
                for (SkillRecord parent : hit.parents) {
                    prompt.append("\nHierarquia: ").append(parent.skillName).append(" — ").append(parent.skillDescription);
                }
                prompt.append("\nHabilidade: ").append(record.skillName)
                        .append("\nDescrição: ").append(record.skillDescription);
                if (record.whenToUse != null && !record.whenToUse.isBlank()) {
                    prompt.append("\nQuando usar: ").append(record.whenToUse);
                }
                if (record.trigger != null && !record.trigger.isBlank()) {
                    prompt.append("\nGatilho: ").append(record.trigger);
                }
            }
        }
        return prompt.toString();
    }

    public static final class SendResult {
        public final boolean success;
        public final String text;
        public final List<RetrievedSkill> retrievedSkills;

        private SendResult(boolean success, String text, List<RetrievedSkill> retrievedSkills) {
            this.success = success;
            this.text = text;
            this.retrievedSkills = List.copyOf(new ArrayList<>(retrievedSkills));
        }

        static SendResult success(String text, List<RetrievedSkill> hits) { return new SendResult(true, text, hits); }
        static SendResult failure(String message, List<RetrievedSkill> hits) { return new SendResult(false, message, hits); }
    }
}
