import { Agent, tool } from '@openai/agents';
import { z } from 'zod';

// Shared memory for inter-agent communication
class SharedMemory {
  constructor() {
    this.data = new Map();
    this.conversationHistory = [];
  }

  set(key, value) {
    this.data.set(key, value);
  }

  get(key) {
    return this.data.get(key);
  }

  addToHistory(agent, message) {
    this.conversationHistory.push({
      agent,
      message,
      timestamp: new Date().toISOString(),
    });
  }

  getHistory() {
    return this.conversationHistory;
  }
}

// Tool for agents to communicate with each other
const communicateTool = tool({
  name: 'communicate_with_agent',
  description: 'Send a message to another agent and get a response',
  inputSchema: z.object({
    targetAgent: z.string().describe('The name of the agent to communicate with'),
    message: z.string().describe('The message to send to the agent'),
  }),
  execute: async ({ targetAgent, message }, { sharedMemory, agentSystem }) => {
    const target = agentSystem.agents[targetAgent.toLowerCase()];
    if (!target) {
      return `Error: Agent "${targetAgent}" not found`;
    }
    
    const response = await target.run(message);
    sharedMemory.addToHistory(targetAgent, { message, response });
    return `Response from ${targetAgent}: ${response}`;
  },
});

// Tool for agents to access shared memory
const memoryTool = tool({
  name: 'access_memory',
  description: 'Read or write data to shared memory',
  inputSchema: z.object({
    action: z.enum(['read', 'write']).describe('Whether to read or write'),
    key: z.string().describe('The key to read or write'),
    value: z.string().optional().describe('The value to write (only for write action)'),
  }),
  execute: async ({ action, key, value }, { sharedMemory }) => {
    if (action === 'read') {
      return `Memory value for "${key}": ${sharedMemory.get(key) || 'not found'}`;
    } else if (action === 'write') {
      sharedMemory.set(key, value);
      return `Stored "${value}" with key "${key}"`;
    }
  },
});

// Research Agent
const researchAgent = new Agent({
  name: 'Researcher',
  instructions: `You are a research agent specialized in gathering and analyzing information.
  You can communicate with other agents to get specialized information.
  Always store your findings in shared memory for other agents to access.`,
  tools: [communicateTool, memoryTool],
});

// Data Analysis Agent
const analysisAgent = new Agent({
  name: 'Analyst',
  instructions: `You are a data analysis agent that processes information and provides insights.
  You can read from shared memory and communicate with other agents for additional data.
  Focus on providing analytical insights and conclusions.`,
  tools: [communicateTool, memoryTool],
});

// Report Writer Agent
const writerAgent = new Agent({
  name: 'Writer',
  instructions: `You are a report writing agent that creates comprehensive reports.
  You can read from shared memory and communicate with other agents for additional information.
  Focus on creating well-structured, clear reports based on available data.`,
  tools: [communicateTool, memoryTool],
});

// Project Manager Agent
const managerAgent = new Agent({
  name: 'Manager',
  instructions: `You are a project manager that coordinates complex tasks between multiple agents.
  You can delegate work to specialized agents and synthesize their outputs.
  Always ensure the final result is comprehensive and well-organized.`,
  tools: [communicateTool, memoryTool],
});

// Advanced Multi-Agent System
class AdvancedMultiAgentSystem {
  constructor() {
    this.sharedMemory = new SharedMemory();
    this.agents = {
      researcher: researchAgent,
      analyst: analysisAgent,
      writer: writerAgent,
      manager: managerAgent,
    };
    
    // Inject shared memory and agent system into tool contexts
    this.setupToolContexts();
  }

  setupToolContexts() {
    // This would typically be done through the SDK's context injection mechanism
    // For now, we'll simulate this by passing context in the execute functions
  }

  async executeComplexTask(task) {
    console.log(`\n🚀 Starting complex task: "${task}"`);
    
    // Step 1: Manager analyzes the task and creates a plan
    const plan = await this.agents.manager.run(
      `Analyze this task and create a step-by-step plan: "${task}"`
    );
    
    console.log(`📋 Manager's Plan: ${plan}`);
    
    // Step 2: Researcher gathers information
    const researchResult = await this.agents.researcher.run(
      `Research information related to: "${task}". Store your findings in shared memory.`
    );
    
    console.log(`🔍 Research Results: ${researchResult}`);
    
    // Step 3: Analyst processes the information
    const analysisResult = await this.agents.analyst.run(
      `Analyze the research data and provide insights. Check shared memory for research findings.`
    );
    
    console.log(`📊 Analysis Results: ${analysisResult}`);
    
    // Step 4: Writer creates the final report
    const report = await this.agents.writer.run(
      `Create a comprehensive report based on the research and analysis. Check shared memory for all available data.`
    );
    
    console.log(`📝 Final Report: ${report}`);
    
    // Step 5: Manager reviews and synthesizes
    const finalResult = await this.agents.manager.run(
      `Review the final report and provide a summary of the complete task execution.`
    );
    
    return {
      task,
      plan,
      researchResult,
      analysisResult,
      report,
      finalResult,
      sharedMemory: this.sharedMemory.data,
      conversationHistory: this.sharedMemory.getHistory(),
    };
  }

  async runCollaborativeExample() {
    console.log('🤖 Advanced Multi-Agent System - Collaborative Example');
    console.log('='.repeat(60));
    
    const complexTask = 'Analyze the impact of artificial intelligence on modern education';
    
    const result = await this.executeComplexTask(complexTask);
    
    console.log('\n🎯 Final Results:');
    console.log(JSON.stringify(result, null, 2));
  }
}

// Agent Communication Example
class AgentCommunicationExample {
  constructor() {
    this.sharedMemory = new SharedMemory();
    this.agents = {
      researcher: researchAgent,
      analyst: analysisAgent,
      writer: writerAgent,
    };
  }

  async demonstrateCommunication() {
    console.log('\n💬 Agent Communication Demonstration');
    console.log('='.repeat(50));
    
    // Agent 1 asks Agent 2 for help
    const response1 = await this.agents.researcher.run(
      'I need help analyzing climate change data. Can you help me understand the trends?'
    );
    
    console.log(`Researcher: ${response1}`);
    
    // Agent 2 responds and asks Agent 3 for additional info
    const response2 = await this.agents.analyst.run(
      'I can help analyze climate data. Let me also ask the writer to help format our findings.'
    );
    
    console.log(`Analyst: ${response2}`);
    
    // Agent 3 provides formatting help
    const response3 = await this.agents.writer.run(
      'I can help format the climate change analysis into a clear report. What specific data do you have?'
    );
    
    console.log(`Writer: ${response3}`);
  }
}

// Main execution
async function main() {
  console.log('🤖 Advanced Multi-Agent System Examples');
  
  // Example 1: Complex task execution
  const advancedSystem = new AdvancedMultiAgentSystem();
  await advancedSystem.runCollaborativeExample();
  
  // Example 2: Agent communication
  const communicationExample = new AgentCommunicationExample();
  await communicationExample.demonstrateCommunication();
}

main().catch(console.error); 