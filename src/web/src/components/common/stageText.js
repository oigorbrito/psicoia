import { containsSourceLanguageText } from "../../locale.js";

const STAGE_LABELS = {
  assessment: ["Avaliação e definição de foco", "Assessment and focus setting"],
  intervention: ["Intervenção", "Intervention"],
  consolidation: ["Consolidação", "Consolidation"],
};

function activeLocale(locale) {
  return locale || (typeof localStorage !== "undefined" && localStorage.getItem("psicoia-locale")) || "pt-BR";
}

export function getStageDisplayLabel(stage, locale) {
  const selectedLocale = activeLocale(locale);
  const labels = STAGE_LABELS[stage?.key];
  if (labels) return labels[selectedLocale === "en" ? 1 : 0];
  if (stage?.label) {
    if (containsSourceLanguageText(stage.label)) {
      return selectedLocale === "en"
        ? `Source-language label (not translated): ${stage.label}`
        : `Rótulo no idioma de origem (não traduzido): ${stage.label}`;
    }
    return stage.label;
  }
  return selectedLocale === "en" ? "Not started" : "Não iniciada";
}
