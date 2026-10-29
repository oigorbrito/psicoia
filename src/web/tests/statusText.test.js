import assert from "node:assert/strict";
import test from "node:test";

import {
  formatVisitLabel,
  getCourseStatusText,
  getVisitStatusText,
} from "../src/components/common/statusText.js";

test("course and visit status helpers map known and unknown values", () => {
  assert.equal(getCourseStatusText("active"), "进行中");
  assert.equal(getCourseStatusText("unknown"), "未知状态");
  assert.equal(getVisitStatusText("closed"), "已结束");
  assert.equal(getVisitStatusText("unknown"), "未知状态");
});

test("visit labels normalize numeric input", () => {
  assert.equal(formatVisitLabel(3), "第 3 次会谈");
  assert.equal(formatVisitLabel("4"), "第 4 次会谈");
  assert.equal(formatVisitLabel(undefined), "第 0 次会谈");
});
