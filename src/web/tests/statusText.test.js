import assert from "node:assert/strict";
import test from "node:test";

import {
  formatVisitLabel,
  getCourseStatusText,
  getVisitStatusText,
} from "../src/components/common/statusText.js";
import { getSchoolDisplayName } from "../src/components/common/schoolText.js";
import { outputLanguageForLocale } from "../src/locale.js";

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

test("visit labels normalize numeric input in both locales", () => {
  assert.equal(formatVisitLabel(3, "pt-BR"), "Sessão 3");
  assert.equal(formatVisitLabel("4", "en"), "Session 4");
  assert.equal(formatVisitLabel(undefined, "pt-BR"), "Sessão 0");
});
