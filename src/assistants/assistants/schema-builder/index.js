import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const schemaBuilderAssistant = {
  systemMessage: fs.readFileSync(path.join(__dirname, "prompt.md"), {
    encoding: "utf-8",
  }),
  saveResult: async function (
    rawString,
    schemaName,
    schemaDescription,
    fileName
  ) {
    let match = rawString.trim().match(/\{.*\}/ms);
    let schemaDefinition = {};
    if (match) {
      schemaDefinition = JSON.parse(match[0]);
    } else {
      console.log("No schema definition found in response");
      return;
    }

    let body = {
      schema_name: schemaName,
      schema_description: schemaDescription,
      schema_definition: schemaDefinition,
    };
    let fileContents = JSON.stringify(body, null, 2);
    fs.writeFileSync(fileName, fileContents);
  },
};
export { schemaBuilderAssistant };
