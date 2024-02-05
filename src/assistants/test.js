import chalk from "chalk";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

import { startThread } from "./thread.js";

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

await runTest();
