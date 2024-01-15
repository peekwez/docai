import { startThread } from "./thread.js";

const runTest = async () => {
  const thread = await startThread({ assistantName: "schema-builder" });

  let firstMessage =
    "Create a schema to extract the name of an employee from a letter of employment";
  let secondMessage = "Add a field for extracting the employee's salary. ";
  secondMessage +=
    "The salary field should be an object with amount and frequency fields.";
  secondMessage +=
    "The frequency can be annually, monthly, biweekly, weekly or hourly";

  console.log("[*] Adding first message to thread");
  console.log(`[*] Message :: ${firstMessage}`);
  console.log("");

  await thread.addMessage(firstMessage);
  await thread.streamResult();

  console.log("[*] Adding second message to thread");
  console.log(`[*] Message :: ${secondMessage}`);
  console.log("");

  await thread.addMessage(secondMessage);
  await thread.streamResult();

  const threadFileName =
    "/Users/kwesi/Desktop/projects/docai/src/agents/tmp/thread-1.json";
  await thread.saveThread(threadFileName);

  const schemaName = "test-loe-schema";
  const schemaDescription =
    "This schema is a schema for extracting data from a letter of employment.";
  const schemaFileName =
    "/Users/kwesi/Desktop/projects/docai/src/agents/tmp/schema-1.json";
  await thread.saveResult(schemaName, schemaDescription, schemaFileName);
  1;
};

await runTest();
