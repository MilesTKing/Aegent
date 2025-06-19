import { Agent, tool } from '@openai/agents';
import { z } from 'zod';

// Agent 1: History Expert
const historyFunFact = tool({
  name: 'history_fun_fact',
  description: 'Give a fun fact about a historical event',
  inputSchema: z.object({
    topic: z.string().describe('Historical topic to get a fun fact about')
  }).strict(),
  execute: async ({ topic }) => {
    const facts = [
      'Sharks are older than trees.',
      'The Great Wall of China is not visible from space with the naked eye.',
      'Cleopatra lived closer to the moon landing than to the building of the Great Pyramid.',
      'The shortest war in history lasted only 38 minutes.',
    ];
    const randomFact = facts[Math.floor(Math.random() * facts.length)];
    return topic ? `Fun fact about ${topic}: ${randomFact}` : randomFact;
  },
});

const historyAgent = new Agent({
  name: 'History Expert',
  instructions: 'You are a knowledgeable history expert. Provide accurate historical information and fun facts.',
  tools: [historyFunFact],
});

// Agent 2: Science Expert
const scienceFact = tool({
  name: 'science_fact',
  description: 'Provide an interesting science fact',
  inputSchema: z.object({
    field: z.string().describe('Scientific field to get a fact about')
  }).strict(),
  execute: async ({ field }) => {
    const facts = [
      'A day on Venus is longer than its year.',
      'The human body contains enough iron to make a 3-inch nail.',
      'Lightning is hotter than the surface of the sun.',
      'There are more atoms in a glass of water than glasses of water in all the oceans.',
    ];
    const randomFact = facts[Math.floor(Math.random() * facts.length)];
    return field ? `Science fact about ${field}: ${randomFact}` : randomFact;
  },
});

const scienceAgent = new Agent({
  name: 'Science Expert',
  instructions: 'You are a science expert. Provide accurate scientific information and interesting facts.',
  tools: [scienceFact],
});

// Agent 3: Math Expert
const calculateTool = tool({
  name: 'calculate',
  description: 'Perform mathematical calculations',
  inputSchema: z.object({
    expression: z.string().describe('The mathematical expression to evaluate'),
  }).strict(),
  execute: async ({ expression }) => {
    try {
      // Note: In a real application, you'd want to use a safer evaluation method
      const result = eval(expression);
      return `The result of ${expression} is ${result}`;
    } catch (error) {
      return `Error calculating ${expression}: ${error.message}`;
    }
  },
});

const mathAgent = new Agent({
  name: 'Math Expert',
  instructions: 'You are a mathematics expert. Help with calculations and mathematical concepts.',
  tools: [calculateTool],
});

// Agent 4: Coordinator Agent
const coordinatorAgent = new Agent({
  name: 'Coordinator',
  instructions: `You are a coordinator that can delegate tasks to specialized agents:
  - History Expert: For historical questions and facts
  - Science Expert: For scientific questions and facts  
  - Math Expert: For mathematical calculations and concepts
  
  When a user asks a question, determine which agent(s) would be best suited to answer it.
  You can also combine responses from multiple agents when appropriate.`,
});

// Multi-Agent System Class
class MultiAgentSystem {
  constructor() {
    this.agents = {
      history: historyAgent,
      science: scienceAgent,
      math: mathAgent,
      coordinator: coordinatorAgent,
    };
  }

  async processQuery(query) {
    console.log(`\n🤖 Processing query: "${query}"`);
    
    // First, let the coordinator analyze the query
    const coordinatorResponse = await this.agents.coordinator.run(
      `Analyze this query and determine which agent(s) should handle it: "${query}"`
    );
    
    console.log(`📋 Coordinator analysis: ${coordinatorResponse}`);
    
    // Determine which agents to use based on the query
    const responses = {};
    
    if (query.toLowerCase().includes('history') || query.toLowerCase().includes('historical')) {
      responses.history = await this.agents.history.run({ topic: query });
    }
    
    if (query.toLowerCase().includes('science') || query.toLowerCase().includes('scientific')) {
      responses.science = await this.agents.science.run({ field: query });
    }
    
    if (query.toLowerCase().includes('math') || query.toLowerCase().includes('calculate') || 
        query.toLowerCase().includes('equation') || /\d/.test(query)) {
      responses.math = await this.agents.math.run({ expression: query });
    }
    
    // If no specific agent was triggered, use the coordinator
    if (Object.keys(responses).length === 0) {
      responses.coordinator = await this.agents.coordinator.run(query);
    }
    
    return {
      query,
      coordinatorAnalysis: coordinatorResponse,
      agentResponses: responses,
    };
  }

  async runInteractiveSession() {
    console.log('🤖 Multi-Agent System Started!');
    console.log('Available agents: History Expert, Science Expert, Math Expert, Coordinator');
    console.log('Type "exit" to quit\n');
    
    // Example queries to demonstrate the system
    const exampleQueries = [
      'Tell me a fun history fact',
      'What\'s an interesting science fact?',
      'Calculate 15 * 23',
      'Give me both a history and science fact',
    ];
    
    for (const query of exampleQueries) {
      const result = await this.processQuery(query);
      console.log('\n📝 Results:');
      console.log(JSON.stringify(result, null, 2));
      console.log('\n' + '='.repeat(50));
    }
  }
}

// Main execution
async function main() {
  const multiAgentSystem = new MultiAgentSystem();
  await multiAgentSystem.runInteractiveSession();
}

main().catch(console.error); 