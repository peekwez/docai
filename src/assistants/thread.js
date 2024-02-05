import fs from "fs";
import uuid4 from "uuid4";
import OpenAI from "openai";

import { Config } from "./utils.js";
import { assistants } from "./assistants/index.js";

const GPT_MODEL = process.env.GPT_MODEL || "gpt-4-1106-preview";
const PARAM_NAME = process.env.PARAM_NAME || "/dev/secret/openai/api_key";

const config = new Config();
const openai = new OpenAI({
  apiKey: await config.getSecretValue(PARAM_NAME),
});

async function startThread({ userId, assistantName, memorySize = 20 }) {
  // Create a new thread object

  const thread = {
    userId: userId || uuid4(),
    threadId: uuid4(),
    assistant: assistants[assistantName],
    memorySize: memorySize,
    chatHistory: [],
    latestResult: {},
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    stream: null,
    saveResult: async function (...props) {
      this.assistant.saveResult(this.latestResult, ...props);
    },
    saveThread: async function (fileName) {
      // Save the thread data to a file or database
      let body = {
        user_id: this.userId,
        thread_id: this.threadId,
        agent_name: this.agentName,
        system_message: this.assistant.systemMessage,
        chat_history: this.chatHistory,
        latest_result: this.latestResult,
        created_at: this.createdAt,
        updated_at: this.updatedAt,
      };
      let fileContents = JSON.stringify(body, null, 2);
      fs.writeFileSync(fileName, fileContents);
    },
    streamResult: async function () {
      if (!this.stream) {
        return;
      }

      // Stream the result from OpenAI
      this.latestResult = "";
      for await (const chunk of this.stream) {
        let result = chunk.choices[0]?.delta?.content || "";
        this.latestResult += result;
        process.stdout.write(result);
      }
      process.stdout.write("\n");

      // Prase JSON string to an object and add the response to the thread
      this.chatHistory.push({
        role: "assistant",
        content: this.latestResult,
      });
      this.updatedAt = new Date().toISOString();
      this.stream = null;
    },
    addMessage: async function (message) {
      // Add a check to make sure the message is not empty
      if (message.trim() === "") {
        return;
      }

      // Add a new user message to the thread
      this.chatHistory.push({ role: "user", content: message });

      // Remove the first two messages if the memory size is exceeded
      if (this.chatHistory.length > this.memorySize) {
        this.chatHistory = this.chatHistory.slice(2);
      }

      // Create messages for OpenAI
      let messages = [
        { role: "system", content: this.assistant.systemMessage },
        ...this.chatHistory,
      ];

      // Send the messages to OpenAI
      this.stream = await openai.chat.completions.create({
        messages: messages,
        model: GPT_MODEL,
        stream: true,
      });
    },
  };

  return thread;
}

export { startThread };
