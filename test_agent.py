 
# test_agent.py - Simple test to understand OpenAgents WorkerAgent
from openagents.agents.worker_agent import WorkerAgent
import asyncio

class TestAgent(WorkerAgent):
    default_agent_id = "test_agent"
    
    async def on_startup(self):
        """Called when agent starts"""
        print("🚀 Test Agent starting up!")
        
        # Try to access workspace
        try:
            ws = self.workspace()
            print(f"✅ Workspace accessed: {ws}")
            
            # Try to post to a channel
            await ws.channel("general").post("Hello from Test Agent!")
            print("✅ Posted message to #general channel")
            
        except Exception as e:
            print(f"❌ Error in startup: {e}")
    
    async def on_channel_post(self, context):
        """Called when someone posts to a channel we're watching"""
        try:
            content = context.incoming_event.payload.get('content', {}).get('text', '')
            channel = context.channel
            
            print(f"📩 Received message in #{channel}: {content}")
            
            if "hello" in content.lower():
                ws = self.workspace()
                await ws.channel(channel).reply(
                    context.incoming_event.id,
                    "Hello! I'm a test agent."
                )
                
        except Exception as e:
            print(f"❌ Error handling message: {e}")

if __name__ == "__main__":
    print("Testing OpenAgents WorkerAgent...")
    agent = TestAgent()
    
    # Try to run
    try:
        asyncio.run(agent.run())
    except Exception as e:
        print(f"❌ Error running agent: {e}")
        print("\nThis tells us what we need to configure...")