import fs from "node:fs";

const path = "C:/Users/hello/.codex/plugins/cache/openai-primary-runtime/presentations/26.805.11740/skills/presentations/assets/builtin_templates/codex-grid-layout-library/artifact-tool-compose/template-registry.json";
const registry = JSON.parse(fs.readFileSync(path, "utf8"));
for (const template of registry.templates) {
  const slots = template.slots
    .filter((slot) => slot.source === "content-token")
    .map((slot) => `${slot.name}:${slot.role}`)
    .join(",");
  console.log([
    template.slideNumber,
    template.templateUse,
    template.layoutFamily,
    template.densityBudget.level,
    slots,
  ].join("\t"));
}
