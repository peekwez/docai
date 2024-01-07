import { startThread } from "./thread.js";

const runTest = async () => {
  const thread = await startThread({ agentName: "schema-builder" });

  let firstMessage =
    "Create a schema to extract the name of an employee from a letter of employment";
  let secondMessage = "Add a field for extracting the employee's salary. ";
  secondMessage +=
    "The salary field should be an object with amount and frequency fields.";
  secondMessage +=
    "The frequency can be annually, monthly, biweekly, weekly or hourly";

  await thread.addMessage(firstMessage);
  await thread.streamResult();

  await thread.addMessage(secondMessage);
  await thread.streamResult();

  await thread.saveThread();
  await thread.saveResult(
    "test-loe-schema",
    "This schema is a schema for extracting data from a letter of employment."
  );
};

export { runTest, startThread };
