const COURSE_STATUS_LABELS = {
  active: "进行中",
  completed: "已完成",
  archived: "已归档",
};

const VISIT_STATUS_LABELS = {
  open: "进行中",
  closed: "已结束",
};

function activeLocale(locale) {
  return locale || (typeof localStorage !== "undefined" && localStorage.getItem("psicoia-locale")) || "pt-BR";
}

export function getCourseStatusText(status, locale) {
  locale = activeLocale(locale);
  const label = COURSE_STATUS_LABELS[status] || "未知状态";
  return locale === "en" ? ({ "进行中": "In progress", "已完成": "Completed", "已归档": "Archived", "未知状态": "Unknown status" }[label]) : ({ "进行中": "Em andamento", "已完成": "Concluído", "已归档": "Arquivado", "未知状态": "Status desconhecido" }[label]);
}

export function getVisitStatusText(status, locale) {
  locale = activeLocale(locale);
  const label = VISIT_STATUS_LABELS[status] || "未知状态";
  return locale === "en" ? ({ "进行中": "In progress", "已结束": "Ended", "未知状态": "Unknown status" }[label]) : ({ "进行中": "Em andamento", "已结束": "Encerrada", "未知状态": "Status desconhecido" }[label]);
}

export function formatVisitLabel(visitNo, locale) {
  locale = activeLocale(locale);
  const normalizedNo = Number(visitNo) || 0;
  return locale === "en" ? `Session ${normalizedNo}` : `Sessão ${normalizedNo}`;
}
