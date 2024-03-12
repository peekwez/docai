import chalk from "chalk";
import path from "path";
import { fileURLToPath } from "url";
import fs from "fs";
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

import { startThread } from "./thread.js";
import { read } from "fs";

const runTest = async () => {
  const assistantName = "schema-builder";
  const thread = await startThread({ assistantName });

  let firstMessage =
    "Create a schema to extract the name of an employee from a letter of employment";
  let secondMessage =
    "Add a field for extracting the employee's salary. " +
    "The salary field should be an object with amount and frequency fields." +
    "The frequency can be annually, monthly, biweekly, weekly or hourly";

  console.log(chalk.cyan("[*] Adding first message to thread"));
  console.log(chalk.magenta(`[*] Message :: ${firstMessage}`));
  console.log("");
  await thread.addMessage(firstMessage);
  await thread.streamResult();

  console.log(chalk.cyan("[*] Adding second message to thread"));
  console.log(chalk.magenta(`[*] Message :: ${secondMessage}`));
  console.log("");
  await thread.addMessage(secondMessage);
  await thread.streamResult();

  const threadFileName = path.join(__dirname, "tmp", "test-thread.json");
  await thread.saveThread(threadFileName);

  const schemaName = "test-loe-schema";
  const schemaDescription =
    "This schema is a schema for extracting data from a letter of employment.";
  const schemaFileName = path.join(__dirname, "tmp", "test-schema.json");
  await thread.saveResult(schemaName, schemaDescription, schemaFileName);
};

// const runTestCRM = async () => {
//   const assistantName = "schema-builder";
//   const thread = await startThread({ assistantName });

//   let firstMessage = fs.readFileSync(schemaFile, "utf8");

//   console.log(chalk.cyan("[*] Adding first message to thread"));
//   console.log("");

//   await thread.addMessage(
//     `Rewrite the JSON schema below. Include all the description examples and create enums where possible: \n${firstMessage}\n`
//   );
//   await thread.streamResult();

//   const threadFileName = path.join(__dirname, "tmp", "test-crm-thread.json");
//   await thread.saveThread(threadFileName);

//   const schemaName = "test-crm-schema";
//   const schemaDescription =
//     "This schema is a schema for extracting data from a customer relationship management software notes.";
//   const schemaFileName = path.join(__dirname, "tmp", "test-crm-schema.json");
//   await thread.saveResult(schemaName, schemaDescription, schemaFileName);
// };

await runTest();
// await runTestCRM();
const data = {
  OK: true,
  result: {
    schema_name: "crm-schema",
    schema_version: "TpnvIH4qAo",
    number_of_tokens: 1112,
  },
};
