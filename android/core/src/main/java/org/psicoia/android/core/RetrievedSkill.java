package org.psicoia.android.core;

import java.util.Collections;
import java.util.List;

/** A catalog hit plus its unchanged score and available parent records. */
public final class RetrievedSkill {
    public final String sect;
    public final int stage;
    public final String catalogType;
    public final double score;
    public final SkillRecord record;
    public final List<SkillRecord> parents;

    RetrievedSkill(
            String sect,
            int stage,
            String catalogType,
            double score,
            SkillRecord record,
            List<SkillRecord> parents) {
        this.sect = sect;
        this.stage = stage;
        this.catalogType = catalogType;
        this.score = score;
        this.record = record;
        this.parents = Collections.unmodifiableList(parents);
    }
}
