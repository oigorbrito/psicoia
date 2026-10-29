export function outputLanguageForLocale(locale) {
  return locale === "en" ? "English" : "Português (Brasil)";
}

export function containsSourceLanguageText(value) {
  return /[\u3400-\u9fff]/u.test(String(value ?? ""));
}

export function sourceLanguageDisclosure(locale) {
  return locale === "en"
    ? "This text includes Chinese and is shown as-is; it has not been translated or validated."
    : "Este texto contém chinês e é exibido como está; não foi traduzido nem validado.";
}
