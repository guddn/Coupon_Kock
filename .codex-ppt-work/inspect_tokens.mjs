import fs from "node:fs";

const path = "C:/Users/hello/.codex/plugins/cache/openai-primary-runtime/presentations/26.805.11740/skills/presentations/assets/builtin_templates/codex-grid-layout-library/artifact-tool-compose/content-tokens.json";
const tokens = JSON.parse(fs.readFileSync(path, "utf8"));
for (const id of ["slide-02", "slide-04", "slide-08", "slide-13", "slide-17", "slide-19", "slide-26"]) {
  console.log(`\n=== ${id} ===`);
  console.log(JSON.stringify(tokens[id], null, 2));
}
