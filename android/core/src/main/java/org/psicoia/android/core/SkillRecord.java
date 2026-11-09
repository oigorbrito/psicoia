package org.psicoia.android.core;

import com.google.gson.annotations.SerializedName;
import java.util.ArrayList;
import java.util.List;

/** A source catalog record. IDs and parent IDs are kept as strings exactly as authored. */
public final class SkillRecord {
    @SerializedName("skill_id") public String skillId = "";
    @SerializedName("skill_name") public String skillName = "";
    @SerializedName("skill_description") public String skillDescription = "";
    @SerializedName("when_to_use") public String whenToUse = "";
    public String trigger = "";
    @SerializedName("parent_ids") public List<String> parentIds = new ArrayList<>();
    public String sect = "";
}
