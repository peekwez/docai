import fs from "fs";
import uuid4 from "uuid4";

const FILE_EXTENSION = ".md";
const PACKAGE_HOME = "/Users/kwesi/Desktop/projects/docai/src/agents";
const PROMPT_DIRECTORY = `${PACKAGE_HOME}/prompts`;
const TMP_DIRECTORY = `${PACKAGE_HOME}/tmp`;

async function saveSchemaBuilderAgentData(
  rawString,
  schemaName,
  schemaDescription
) {
  let match = rawString.trim().match(/\{.*\}/ms);
  let schemaDefinition = {};
  if (match) {
    schemaDefinition = JSON.parse(match[0]);
  } else {
    console.log("No schema definition found in response");
    return;
  }

  let id = uuid4();
  let fileName = `${TMP_DIRECTORY}/schema-${id}.json`;
  let body = {
    schema_name: schemaName,
    schema_description: schemaDescription,
    schema_definition: schemaDefinition,
  };
  let fileContents = JSON.stringify(body, null, 2);
  fs.writeFileSync(fileName, fileContents);
}

const agentSaveResultFunctions = {
  "schema-builder": saveSchemaBuilderAgentData,
};

async function getAgentProperties() {
  // Get all markdown files in the prompts directory
  // and return them as a dictionary of file name to file contents

  var files = fs.readdirSync(`${PROMPT_DIRECTORY}`);
  var textFiles = files.filter((file) => file.endsWith(FILE_EXTENSION));

  var agentProps = {};
  textFiles.forEach((file) => {
    let content = fs.readFileSync(`${PROMPT_DIRECTORY}/${file}`, "utf-8");
    let fileName = file.replace(FILE_EXTENSION, "");
    agentProps[fileName] = {
      systemMessage: content,
      saveResult: agentSaveResultFunctions[fileName],
    };
  });

  return agentProps;
}

const agentProperties = await getAgentProperties();
export { agentProperties };
