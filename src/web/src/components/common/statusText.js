import { t } from "../../i18n";

const COURSE_STATUS_LABELS = {
  active: "In progress",
  completed: "Completed",
  archived: "Archived",
};

const VISIT_STATUS_LABELS = {
  open: "In progress",
  closed: "Ended",
};

export function getCourseStatusText(status, locale) {
  return t(COURSE_STATUS_LABELS[status] || "Unknown status", locale);
}

export function getVisitStatusText(status, locale) {
  return t(VISIT_STATUS_LABELS[status] || "Unknown status", locale);
}

export function formatVisitLabel(visitNo, locale) {
  const normalizedNo = Number(visitNo) || 0;
  return t("Session {number}", locale, { number: normalizedNo });
}
