const SCHOOL_DISPLAY_NAME_MAP = {
  behavioral: "行为疗法 (BT)",
  cbt: "认知行为疗法 (CBT)",
  humanistic: "人本-存在主义疗法 (HET)",
  psychodynamic: "心理动力学疗法 (PDT)",
  postmodern: "后现代主义疗法 (PMT)",
};

const LOCALIZED_NAMES = {
  behavioral: ["Terapia comportamental (BT)", "Behavioral therapy (BT)"],
  cbt: ["Terapia cognitivo-comportamental (CBT)", "Cognitive behavioral therapy (CBT)"],
  humanistic: ["Terapia humanista-existencial (HET)", "Humanistic-existential therapy (HET)"],
  psychodynamic: ["Terapia psicodinâmica (PDT)", "Psychodynamic therapy (PDT)"],
  postmodern: ["Terapia pós-moderna (PMT)", "Postmodern therapy (PMT)"],
};

export function getSchoolDisplayName(school, locale) {
  if (!school) return locale === "en" ? "Not selected" : "Não selecionada";
  const selectedLocale = locale || (typeof localStorage !== "undefined" && localStorage.getItem("psicoia-locale")) || "pt-BR";
  const localized = LOCALIZED_NAMES[school.id];
  if (localized) return localized[selectedLocale === "en" ? 1 : 0];
  const mapped = SCHOOL_DISPLAY_NAME_MAP[school.id];
  if (mapped) return mapped;
  return school.name || (selectedLocale === "en" ? "Not selected" : "Não selecionada");
}
