from datetime import timedelta

from temporalio import workflow


@workflow.defn
class AgentWorkflow:
    @workflow.run
    async def run(self, data: dict):
        """
        ReAct-style agent workflow using Temporal.

        Iteratively:
        1. Calls LLM
        2. Executes tool if requested
        3. Appends observation
        4. Repeats until final answer
        """

        system_prompt = {
            "role": "system",
            "content": data["system_prompt"]
        }

        # Conversation history
        messages = [
            system_prompt,
            {"role": "user", "content": data["input"]}
        ]

        MAX_STEPS = 10  # Prevent infinite loop

        for step in range(MAX_STEPS):

            # Step 1: Call LLM
            llm_response = await workflow.execute_activity(
                "call_llm_activity",
                messages,
                start_to_close_timeout=timedelta(seconds=30),
            )

            # Step 2: Check if tool is requested
            if llm_response["type"] == "tool_call":

                tool_name = llm_response["tool_name"]
                arguments = llm_response["arguments"]

                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": f"call_{step}",
                            "type": "function",      
                            "function": {            
                                "name": tool_name,
                                "arguments": arguments,
                            },
                        }
                    ]
                })

                # Step 3: Execute tool
                tool_result = await workflow.execute_activity(
                    "run_tool_activity",
                    {
                        "tool_name": tool_name,
                        "arguments": arguments,
                    },
                    start_to_close_timeout=timedelta(seconds=60),
                )

                # Step 4: Append observation
                messages.append({
                    "role": "tool",
                    "tool_call_id": f"call_{step}",  
                    "content": f"Observation:\n{tool_result}",
                })

            else:
                # 5. Step 5: Return final result
                return llm_response["content"]

        # Fallback if max steps exceeded
        return "Failed to complete within step limit."