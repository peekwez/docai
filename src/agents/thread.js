import fs from "fs";
import uuid4 from "uuid4";
import OpenAI from "openai";

import { getAgentProperties } from "./agents.js";

const openai = new OpenAI();

const GPT_MODEL = "gpt-4-1106-preview";
const USER_ROLE = "user";
const SYSTEM_ROLE = "system";
const ASSISTANT_ROLE = "assistant";

async function startThread({ userId, agentName, memorySize = 20 }) {
  // Create a new thread object

  // Get the agent properties
  const agentProps = await getAgentProperties();
  const { systemMessage, saveResult: saveAgentResult } = agentProps[agentName];

  // Create the thread object
  const thread = {
    userId: userId || uuid4(),
    threadId: uuid4(),
    agentName: agentName,
    memorySize: memorySize,
    systemMessage: systemMessage,
    chatHistory: [],
    latestResult: {},
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    stream: null,
    saveResult: async function (...props) {
      saveAgentResult(this.latestResult, ...props);
    },
    saveThread: async function () {
      // Save the thread data to a file or database
      let fileName = `thread-${this.threadId}.json`;
      let body = {
        user_id: this.userId,
        thread_id: this.threadId,
        agent_name: this.agentName,
        system_message: this.systemMessage,
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
        this.latestResult += chunk.choices[0]?.delta?.content || "";
        process.stdout.write(chunk.choices[0]?.delta?.content || "");
      }
      process.stdout.write("\n");

      // Prase JSON string to an object and add the response to the thread
      this.chatHistory.push({
        role: ASSISTANT_ROLE,
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
      this.chatHistory.push({ role: USER_ROLE, content: message });

      // Remove the first two messages if the memory size is exceeded
      if (this.chatHistory.length > this.memorySize) {
        this.chatHistory = this.chatHistory.slice(2);
      }

      // Create messages for OpenAI
      let messages = [
        { role: SYSTEM_ROLE, content: this.systemMessage },
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
