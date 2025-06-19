# Multi-Agent System with OpenAI Agent SDK

This project demonstrates how to create sophisticated multi-agent systems using the OpenAI Agent SDK. It includes multiple examples showing different approaches to agent collaboration and communication.

## Current Status

⚠️ **Important Note**: The OpenAI Agent SDK (v0.0.8) currently has a known issue with tool schema validation. The `tool()` function throws an error: "Input type is not a ZodObject or a valid JSON schema" even with valid schemas. This affects all examples that use tools.

**Working Examples:**
- `multi-agent-no-tools.js` - Multi-agent system without tools (fully functional)
- `test-with-run-function.js` - Basic agent example (requires API key)

**Examples with Known Issues:**
- `multi-agent-system.js` - Uses tools (schema validation error)
- `advanced-multi-agent.js` - Uses tools (schema validation error)

## Files Overview

### 1. `OpenaiExample` (Original)
- Basic single agent example
- Simple history fact tool
- Good starting point for understanding the SDK

### 2. `multi-agent-no-tools.js` ✅ **WORKING**
- **Basic Multi-Agent System (No Tools)**
- Four specialized agents: History Expert, Science Expert, Math Expert, and Coordinator
- Demonstrates task delegation and agent coordination
- Shows how different agents can handle different types of queries
- Uses the correct `run()` function from the SDK

### 3. `multi-agent-system.js` ⚠️ **TOOL ISSUES**
- **Basic Multi-Agent System with Tools**
- Same agents as above but with tools
- Currently fails due to tool schema validation issues

### 4. `advanced-multi-agent.js` ⚠️ **TOOL ISSUES**
- **Advanced Multi-Agent System**
- Agents with shared memory and inter-agent communication
- Collaborative task execution
- Research → Analysis → Writing → Management workflow
- Currently fails due to tool schema validation issues

## Key Concepts Demonstrated

### 1. Agent Specialization
Each agent has a specific role and expertise:
- **History Expert**: Historical facts and information
- **Science Expert**: Scientific facts and concepts
- **Math Expert**: Mathematical calculations
- **Coordinator**: Task delegation and coordination

### 2. Task Delegation
The system can:
- Analyze incoming queries
- Determine which agent(s) should handle the task
- Coordinate multiple agents for complex tasks
- Synthesize results from multiple agents

### 3. Correct API Usage
- Uses the `run()` function exported from `@openai/agents`
- Proper agent instantiation and configuration
- Error handling for API key requirements

## Running the Examples

### Prerequisites
```bash
npm install
```

### Set up OpenAI API Key
You'll need an OpenAI API key to run the agents:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or create a `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

### Working Multi-Agent System (No Tools)
```bash
node multi-agent-no-tools.js
```

This will run through example queries demonstrating:
- History queries → History Expert
- Science queries → Science Expert  
- Math queries → Math Expert
- Complex queries → Coordinator

### Basic Agent Test
```bash
node test-with-run-function.js
```

This demonstrates:
- Basic agent functionality
- Correct API usage
- Error handling

## Architecture Patterns

### 1. Coordinator Pattern
- One agent acts as a coordinator
- Analyzes incoming requests
- Delegates to appropriate specialized agents
- Synthesizes responses

### 2. Specialized Agent Pattern
- Each agent has a specific domain expertise
- Agents can be called independently
- Enables focused, high-quality responses

## Known Issues and Workarounds

### Tool Schema Validation Error
**Error**: `Input type is not a ZodObject or a valid JSON schema`

**Cause**: The OpenAI Agent SDK v0.0.8 has a bug in the tool schema validation system.

**Workarounds**:
1. **Use agents without tools** (recommended for now)
2. **Wait for SDK updates** that fix the schema validation
3. **Use alternative agent frameworks** like LangChain or AutoGen

### API Usage
**Correct way to run agents**:
```javascript
import { Agent, run } from '@openai/agents';

const agent = new Agent({
  name: 'My Agent',
  instructions: 'Your instructions here',
});

const result = await run(agent, 'Your query here');
```

**Incorrect way** (will fail):
```javascript
// This doesn't work
const result = await agent.run('Your query here');
```

## Customization Ideas

### 1. Add New Agents
```javascript
const newAgent = new Agent({
  name: 'Your Agent Name',
  instructions: 'Your agent instructions',
});
```

### 2. Extend the Multi-Agent System
```javascript
class ExtendedMultiAgentSystem extends MultiAgentSystem {
  constructor() {
    super();
    this.agents.custom = new Agent({
      name: 'Custom Agent',
      instructions: 'Your custom instructions',
    });
  }
}
```

## Best Practices

### 1. Agent Design
- Give each agent a clear, specific role
- Provide detailed instructions
- Use descriptive names

### 2. Error Handling
- Always wrap agent calls in try-catch blocks
- Handle API key errors gracefully
- Provide helpful error messages

### 3. Performance
- Consider agent execution order
- Implement caching where appropriate
- Monitor agent response times

## Next Steps

1. **Monitor SDK Updates**: Check for new versions that fix tool schema issues
2. **Add Real API Integration**: Connect agents to external APIs for real data
3. **Implement Authentication**: Add proper API key management
4. **Add Persistence**: Store agent conversations and data in a database
5. **Create Web Interface**: Build a web UI for interacting with agents
6. **Add Monitoring**: Implement logging and monitoring for agent performance

## Troubleshooting

### Common Issues
1. **Agent not responding**: Check agent instructions and API key
2. **Tool schema errors**: Use agents without tools until SDK is fixed
3. **API key errors**: Ensure OPENAI_API_KEY is set correctly

### Debugging Tips
1. Enable detailed logging
2. Check agent conversation history
3. Verify API key configuration
4. Test with simple examples first

## Resources

- [OpenAI Agent SDK Documentation](https://github.com/openai/agents)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Multi-Agent Systems Research](https://en.wikipedia.org/wiki/Multi-agent_system) 