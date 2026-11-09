package org.psicoia.android.core;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import java.lang.reflect.Type;
import java.text.Normalizer;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeSet;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Offline BM25 index over the bundled PT-BR micro-skill records. */
public final class CatalogIndex {
    public static final int EXPECTED_SOURCE_RECORDS = 5158;
    private static final int EXPECTED_SOURCE_FILES = 30;
    private static final double K1 = 1.2;
    private static final double B = 0.75;
    private static final Pattern TOKEN = Pattern.compile("[\\p{L}\\p{N}]+");
    private static final Pattern CATALOG_PATH = Pattern.compile(
            "(?:^|.*/)sect/([a-z]+)/stage([1-3])/(meta|micro)_skills\\.pt-BR\\.json$");
    private static final Set<String> STOP_WORDS = Set.of(
            "a", "ao", "aos", "as", "com", "como", "da", "das", "de", "do", "dos",
            "e", "em", "entre", "essa", "esse", "esta", "este", "eu", "na", "nas",
            "no", "nos", "o", "os", "ou", "para", "por", "que", "se", "sem", "um", "uma");
    private static final Type RECORD_MAP_TYPE = new TypeToken<Map<String, SkillRecord>>() {}.getType();

    private final List<IndexedRecord> microRecords;
    private final Map<String, SkillRecord> metaRecords;
    private final Map<String, List<Posting>> postings;
    private final Map<String, Integer> documentCounts;
    private final Map<String, Double> averageLengths;
    private final int sourceRecordCount;

    private CatalogIndex(
            List<IndexedRecord> microRecords,
            Map<String, SkillRecord> metaRecords,
            int sourceRecordCount) {
        this.microRecords = Collections.unmodifiableList(new ArrayList<>(microRecords));
        this.metaRecords = Collections.unmodifiableMap(new LinkedHashMap<>(metaRecords));
        this.sourceRecordCount = sourceRecordCount;
        this.postings = new HashMap<>();
        this.documentCounts = new HashMap<>();
        this.averageLengths = new HashMap<>();

        Map<String, Integer> totalLengths = new HashMap<>();
        for (int i = 0; i < this.microRecords.size(); i++) {
            IndexedRecord indexed = this.microRecords.get(i);
            String scope = scope(indexed.sect, indexed.stage);
            documentCounts.merge(scope, 1, Integer::sum);
            totalLengths.merge(scope, indexed.tokenCount, Integer::sum);
            for (Map.Entry<String, Integer> term : indexed.termFrequencies.entrySet()) {
                postings.computeIfAbsent(term.getKey(), ignored -> new ArrayList<>())
                        .add(new Posting(i, term.getValue()));
            }
        }
        for (Map.Entry<String, Integer> count : documentCounts.entrySet()) {
            averageLengths.put(count.getKey(), (double) totalLengths.get(count.getKey()) / count.getValue());
        }
    }

    /** Input keys are source-relative asset paths; input JSON is never rewritten. */
    public static CatalogIndex fromJsonFiles(Map<String, String> files) {
        Objects.requireNonNull(files, "files");
        if (files.size() != EXPECTED_SOURCE_FILES) {
            throw new IllegalArgumentException("Expected 30 PT-BR catalog files; got " + files.size());
        }

        Gson gson = new Gson();
        List<IndexedRecord> micro = new ArrayList<>();
        Map<String, SkillRecord> meta = new LinkedHashMap<>();
        int records = 0;
        for (Map.Entry<String, String> file : files.entrySet()) {
            Matcher path = CATALOG_PATH.matcher(file.getKey().replace('\\', '/'));
            if (!path.matches()) {
                throw new IllegalArgumentException("Unexpected PT-BR catalog path: " + file.getKey());
            }
            String sect = path.group(1);
            int stage = Integer.parseInt(path.group(2));
            String catalogType = path.group(3);
            Map<String, SkillRecord> parsed = gson.fromJson(file.getValue(), RECORD_MAP_TYPE);
            if (parsed == null || parsed.isEmpty()) {
                throw new IllegalArgumentException("Empty or invalid catalog: " + file.getKey());
            }
            for (Map.Entry<String, SkillRecord> entry : parsed.entrySet()) {
                SkillRecord record = entry.getValue();
                if (record == null || !entry.getKey().equals(record.skillId)) {
                    throw new IllegalArgumentException("Catalog key/skill_id mismatch in " + file.getKey());
                }
                if (record.parentIds == null) {
                    throw new IllegalArgumentException("Missing parent_ids for " + file.getKey() + ":" + entry.getKey());
                }
                if (record.sect != null && !record.sect.isEmpty() && !sect.equals(record.sect)) {
                    throw new IllegalArgumentException("Catalog sect mismatch in " + file.getKey() + ":" + entry.getKey());
                }
                records++;
                if ("meta".equals(catalogType)) {
                    meta.put(recordKey(sect, stage, record.skillId), record);
                } else {
                    micro.add(new IndexedRecord(sect, stage, record, tokenize(textFor(record))));
                }
            }
        }
        if (records != EXPECTED_SOURCE_RECORDS) {
            throw new IllegalArgumentException("Expected 5158 source records; got " + records);
        }
        if (micro.isEmpty()) {
            throw new IllegalArgumentException("No micro-skill records loaded");
        }
        return new CatalogIndex(micro, meta, records);
    }

    public List<RetrievedSkill> search(String query, String sect, int stage, int topK) {
        if (query == null || query.isBlank() || sect == null || sect.isBlank() || stage < 1 || stage > 3 || topK <= 0) {
            return List.of();
        }
        Map<String, Integer> queryTerms = tokenize(query);
        if (queryTerms.isEmpty()) return List.of();

        String scope = scope(sect, stage);
        int corpusSize = documentCounts.getOrDefault(scope, 0);
        double averageLength = averageLengths.getOrDefault(scope, 0.0);
        if (corpusSize == 0 || averageLength <= 0) return List.of();

        Map<Integer, Double> scores = new HashMap<>();
        for (Map.Entry<String, Integer> queryTerm : queryTerms.entrySet()) {
            List<Posting> termPostings = postings.getOrDefault(queryTerm.getKey(), List.of());
            int documentFrequency = 0;
            for (Posting posting : termPostings) {
                IndexedRecord doc = microRecords.get(posting.documentIndex);
                if (doc.sect.equals(sect) && doc.stage == stage) documentFrequency++;
            }
            if (documentFrequency == 0) continue;
            double idf = Math.log(1.0 + (corpusSize - documentFrequency + 0.5) / (documentFrequency + 0.5));
            for (Posting posting : termPostings) {
                IndexedRecord doc = microRecords.get(posting.documentIndex);
                if (!doc.sect.equals(sect) || doc.stage != stage) continue;
                double tf = posting.termFrequency;
                double denominator = tf + K1 * (1.0 - B + B * doc.tokenCount / averageLength);
                double contribution = idf * (tf * (K1 + 1.0) / denominator) * queryTerm.getValue();
                scores.merge(posting.documentIndex, contribution, Double::sum);
            }
        }

        List<Map.Entry<Integer, Double>> ranked = new ArrayList<>(scores.entrySet());
        ranked.sort(Comparator.<Map.Entry<Integer, Double>>comparingDouble(Map.Entry::getValue).reversed()
                .thenComparing(entry -> microRecords.get(entry.getKey()).record.skillId));
        List<RetrievedSkill> result = new ArrayList<>();
        for (Map.Entry<Integer, Double> entry : ranked.subList(0, Math.min(topK, ranked.size()))) {
            IndexedRecord doc = microRecords.get(entry.getKey());
            List<SkillRecord> parents = new ArrayList<>();
            for (String parentId : doc.record.parentIds) {
                SkillRecord parent = metaRecords.get(recordKey(doc.sect, doc.stage, parentId));
                if (parent != null) parents.add(parent);
            }
            result.add(new RetrievedSkill(doc.sect, doc.stage, "micro", entry.getValue(), doc.record, parents));
        }
        return Collections.unmodifiableList(result);
    }

    public int getSourceRecordCount() { return sourceRecordCount; }
    public int getMicroRecordCount() { return microRecords.size(); }
    public int getMetaRecordCount() { return metaRecords.size(); }

    private static String textFor(SkillRecord r) {
        return String.join(" ",
                Objects.toString(r.skillName, ""),
                Objects.toString(r.skillDescription, ""),
                Objects.toString(r.whenToUse, ""),
                Objects.toString(r.trigger, ""));
    }

    private static Map<String, Integer> tokenize(String text) {
        String normalized = Normalizer.normalize(text == null ? "" : text, Normalizer.Form.NFD)
                .replaceAll("\\p{M}+", "").toLowerCase(Locale.ROOT);
        Matcher matcher = TOKEN.matcher(normalized);
        Map<String, Integer> frequencies = new HashMap<>();
        while (matcher.find()) {
            String token = matcher.group();
            if (token.length() > 1 && !STOP_WORDS.contains(token)) frequencies.merge(token, 1, Integer::sum);
        }
        return frequencies;
    }

    private static String scope(String sect, int stage) { return sect + "/" + stage; }
    private static String recordKey(String sect, int stage, String id) { return sect + "/" + stage + "/" + id; }

    private static final class IndexedRecord {
        final String sect;
        final int stage;
        final SkillRecord record;
        final Map<String, Integer> termFrequencies;
        final int tokenCount;
        IndexedRecord(String sect, int stage, SkillRecord record, Map<String, Integer> tf) {
            this.sect = sect;
            this.stage = stage;
            this.record = record;
            this.termFrequencies = tf;
            this.tokenCount = tf.values().stream().mapToInt(Integer::intValue).sum();
        }
    }

    private static final class Posting {
        final int documentIndex;
        final int termFrequency;
        Posting(int documentIndex, int termFrequency) {
            this.documentIndex = documentIndex;
            this.termFrequency = termFrequency;
        }
    }
}
