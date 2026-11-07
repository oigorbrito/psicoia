import test from "node:test";
import assert from "node:assert/strict";
import { getLocale, getOutputLanguage, t } from "../src/i18n.js";

test("UI locales map to supported model output language labels", () => {
  assert.equal(getOutputLanguage("en"), "English");
  assert.equal(getOutputLanguage("pt-BR"), "Português (Brasil)");
});

test("Brazilian Portuguese is the default locale", () => {
  assert.equal(getLocale(), "pt-BR");
});

test("English is the source locale", () => {
  assert.equal(t("Create course", "en"), "Create course");
});

test("Brazilian Portuguese translations interpolate variables", () => {
  assert.equal(t("Start session {number}", "pt-BR", { number: 4 }), "Iniciar sessão 4");
  assert.equal(
    t("Signed in: {username}", "pt-BR", { username: "Ana" }),
    "Conectado como: Ana",
  );
});

test("Chinese backend error details display in the selected interface language", () => {
  assert.equal(t("用户已存在", "en"), "This username is already registered.");
  assert.equal(t("用户已存在", "pt-BR"), "Este nome de usuário já está cadastrado.");
  assert.equal(t("用户名或密码错误", "en"), "Incorrect username or password.");
  assert.equal(t("用户名或密码错误", "pt-BR"), "Nome de usuário ou senha incorretos.");
});

test("Unknown copy falls back to the source text", () => {
  assert.equal(t("Unmapped source string", "pt-BR"), "Unmapped source string");
});

test("Unsupported locale falls back to English", () => {
  assert.equal(t("Create course", "es"), "Create course");
});
