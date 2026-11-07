import { t } from "../../i18n";

const SCHOOL_DISPLAY_NAME_MAP = {
  behavioral: "Behavior Therapy (BT)",
  cbt: "Cognitive Behavioral Therapy (CBT)",
  humanistic: "Humanistic-Existential Therapy (HET)",
  psychodynamic: "Psychodynamic Therapy (PDT)",
  postmodern: "Postmodern Therapy (PMT)",
};

export function getSchoolDisplayName(school, locale) {
  if (!school) return t("Not selected", locale);
  const mapped = SCHOOL_DISPLAY_NAME_MAP[school.id];
  if (mapped) return t(mapped, locale);
  return t(school.name || "Not selected", locale);
}
