import assert from "node:assert/strict";
import test from "node:test";

import {
  formatVisitLabel,
  getCourseStatusText,
  getVisitStatusText,
} from "../src/components/common/statusText.js";
import { getSchoolDisplayName } from "../src/components/common/schoolText.js";
import { getStageDisplayLabel } from "../src/components/common/stageText.js";
import { containsSourceLanguageText, outputLanguageForLocale } from "../src/locale.js";

test("course and visit statuses have PT-BR and English labels with unknown fallbacks", () => {
  assert.equal(getCourseStatusText("active", "pt-BR"), "Em andamento");
  assert.equal(getCourseStatusText("completed", "en"), "Completed");
  assert.equal(getCourseStatusText("unknown", "pt-BR"), "Status desconhecido");
  assert.equal(getVisitStatusText("closed", "en"), "Ended");
  assert.equal(getVisitStatusText("unknown", "pt-BR"), "Status desconhecido");
});

test("UI locale maps to the existing response-language API enum", () => {
  assert.equal(outputLanguageForLocale("pt-BR"), "Português (Brasil)");
  assert.equal(outputLanguageForLocale("en"), "English");
  assert.equal(outputLanguageForLocale("unexpected"), "Português (Brasil)");
});

test("school display labels are localized without changing stable ids", () => {
  const school = { id: "cbt", name: "认知行为疗法 (CBT)" };
  assert.equal(getSchoolDisplayName(school, "pt-BR"), "Terapia cognitivo-comportamental (CBT)");
  assert.equal(getSchoolDisplayName(school, "en"), "Cognitive behavioral therapy (CBT)");
});

test("CJK stage data from the API renders through the stable PT-BR and EN stage keys", () => {
  const assessmentFromApi = { key: "assessment", label: "\u4e2d\u6587", desc: "\u4e2d\u6587" };
  assert.equal(getStageDisplayLabel(assessmentFromApi, "pt-BR"), "Avaliação e definição de foco");
  assert.equal(getStageDisplayLabel(assessmentFromApi, "en"), "Assessment and focus setting");
  assert.equal(getStageDisplayLabel({ key: "legacy", label: "Legacy stage" }, "en"), "Legacy stage");
});

test("untranslated source-language labels stay visible with an explicit marker", () => {
  assert.equal(containsSourceLanguageText("阶段标签"), true);
  assert.equal(containsSourceLanguageText("Assessment"), false);
  assert.equal(
    getStageDisplayLabel({ key: "legacy", label: "旧阶段" }, "pt-BR"),
    "Rótulo no idioma de origem (não traduzido): 旧阶段",
  );
  assert.equal(
    getSchoolDisplayName({ id: "unknown", name: "未知疗法" }, "en"),
    "Source-language label (not translated): 未知疗法",
  );
});

test("visit labels normalize numeric input in both locales", () => {
  assert.equal(formatVisitLabel(3, "pt-BR"), "Sessão 3");
  assert.equal(formatVisitLabel("4", "en"), "Session 4");
  assert.equal(formatVisitLabel(undefined, "pt-BR"), "Sessão 0");
});
