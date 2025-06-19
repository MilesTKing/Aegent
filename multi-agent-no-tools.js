import { Agent, run } from '@openai/agents';

// Agent 1: History Expert
const historyAgent = new Agent({
  name: 'History Expert',
  instructions: 'You are a knowledgeable history expert. Provide accurate historical information and fun facts. When asked about history, give detailed and interesting responses.',
});

// Agent 2: Science Expert
const scienceAgent = new Agent({
  name: 'Science Expert',
  instructions: 'You are a science expert. Provide accurate scientific information and interesting facts. When asked about science, give detailed and engaging responses.',
});

// Agent 3: Math Expert
const mathAgent = new Agent({
  name: 'Math Expert',
  instructions: 'You are a mathematics expert. Help with calculations and mathematical concepts. When asked about math, provide clear explanations and step-by-step solutions.',
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
    const coordinatorResponse = await run(this.agents.coordinator, 
      `Analyze this query and determine which agent(s) should handle it: "${query}"`
    );
    
    console.log(`📋 Coordinator analysis: ${coordinatorResponse}`);
    
    // Determine which agents to use based on the query
    const responses = {};
    
    if (query.toLowerCase().includes('history') || query.toLowerCase().includes('historical')) {
      responses.history = await run(this.agents.history, query);
    }
    
    if (query.toLowerCase().includes('science') || query.toLowerCase().includes('scientific')) {
      responses.science = await run(this.agents.science, query);
    }
    
    if (query.toLowerCase().includes('math') || query.toLowerCase().includes('calculate') || 
        query.toLowerCase().includes('equation') || /\d/.test(query)) {
      responses.math = await run(this.agents.math, query);
    }
    
    // If no specific agent was triggered, use the coordinator
    if (Object.keys(responses).length === 0) {
      responses.coordinator = await run(this.agents.coordinator, query);
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
    console.log('Note: This version runs without tools due to SDK compatibility issues');
    console.log('Type "exit" to quit\n');
    
    // Example queries to demonstrate the system
    const exampleQueries = [
      'Tell me a fun history fact',
      'What\'s an interesting science fact?',
      'Explain how to solve a quadratic equation',
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
  try {
    const multiAgentSystem = new MultiAgentSystem();
    await multiAgentSystem.runInteractiveSession();
  } catch (error) {
    console.error('❌ Error:', error.message);
    if (error.message.includes('OPENAI_API_KEY')) {
      console.log('\n💡 To run this example, you need to set your OpenAI API key:');
      console.log('export OPENAI_API_KEY="your-api-key-here"');
      console.log('Or create a .env file with: OPENAI_API_KEY=your-api-key-here');
    }
  }
}

main(); 