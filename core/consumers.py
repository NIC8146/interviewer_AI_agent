from distutils.command import config
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from langchain_core.messages import HumanMessage
from asgiref.sync import async_to_sync, sync_to_async
import json
from core.models import Message, candidate, CandidateInfo
from langgraph.types import Command
from agent_engine.workflow.chatworkflow import chatbot, initial_state
from agent_engine.prompt import chatSystemPrompt
from langchain_core.messages import SystemMessage

class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "some_room"
        self.room_group_name = "some_group"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        user_id = self.scope["url_route"]["kwargs"]["pk"]
        self.config = {"configurable": {"thread_id": user_id}}
        started = chatbot.get_state(self.config).values.get("started", False)

        if not started:
            aimessage = chatbot.invoke(initial_state, config=self.config)['process_explainations'][-1].content
            ai_response = {
                "AiMessage": aimessage,
                "userID": user_id
            }
            candidate_instance = await sync_to_async(candidate.objects.get)(user_id=user_id)
            await sync_to_async(Message.objects.create)(
                sender='bot', text=aimessage, candidate=candidate_instance
            )
            await self.send(text_data=json.dumps(ai_response))


    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        # If it's a human message
        if "HumanMessage" in data:
            human_msg = data["HumanMessage"]
            user_id = data.get("userID")
            candidate_instance = await sync_to_async(candidate.objects.get)(user_id=user_id)
            await sync_to_async(Message.objects.create)(
                sender='user', text=human_msg, candidate=candidate_instance
            )
            if chatbot.get_state(self.config).values["processexplained"]:
                # aimessage = chatbot.invoke({ 'messages': [HumanMessage(content=human_msg)] }, config=self.config)
                aimessage = chatbot.invoke(Command(resume=human_msg), config=self.config)
            else:
                # aimessage = chatbot.invoke({ 'process_explainations': [HumanMessage(content=human_msg)] }, config=self.config)
                aimessage = chatbot.invoke(Command(resume=human_msg), config=self.config)

            if chatbot.get_state(self.config).values["processexplained"]:
                message = aimessage['messages'][-1].content
            else:
                message = aimessage['process_explainations'][-1].content
            # Respond back with an AiMessage
            ai_response = {
                "AiMessage": message,
                "userID": user_id
            }
            
            candidate_instance = await sync_to_async(candidate.objects.get)(user_id=user_id)
            await sync_to_async(Message.objects.create)(
                sender='bot', text=message, candidate=candidate_instance
            )
            await self.send(text_data=json.dumps(ai_response))
