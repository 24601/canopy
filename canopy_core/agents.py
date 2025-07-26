"""
MassAgent implementations that wrap the existing agent backends.

This module provides MassAgent-compatible wrappers for the existing
OpenAI, Gemini, and Grok agent implementations.
"""

import os
from typing import Callable, Dict, List, Optional

from dotenv import load_dotenv

from .agent import MassAgent
from .types import ModelConfig, TaskInput  # noqa: TC001

load_dotenv()


class OpenAIMassAgent(MassAgent):
    """MassAgent wrapper for OpenAI agent implementation."""

    def __init__(
        self,
        agent_id: int,
        orchestrator=None,
        model_config: Optional[ModelConfig] = None,
        stream_callback: Optional[Callable] = None,
        **kwargs,
    ):
        # Pass all configuration to parent, including agent_type
        super().__init__(
            agent_id=agent_id,
            orchestrator=orchestrator,
            model_config=model_config,
            stream_callback=stream_callback,
            **kwargs,
        )


class GrokMassAgent(OpenAIMassAgent):
    """MassAgent wrapper for Grok agent implementation."""

    def __init__(
        self,
        agent_id: int,
        orchestrator=None,
        model_config: Optional[ModelConfig] = None,
        stream_callback: Optional[Callable] = None,
        **kwargs,
    ):
        # Pass all configuration to parent, including agent_type
        super().__init__(
            agent_id=agent_id,
            orchestrator=orchestrator,
            model_config=model_config,
            stream_callback=stream_callback,
            **kwargs,
        )


class GeminiMassAgent(OpenAIMassAgent):
    """MassAgent wrapper for Gemini agent implementation."""

    def __init__(
        self,
        agent_id: int,
        orchestrator=None,
        model_config: Optional[ModelConfig] = None,
        stream_callback: Optional[Callable] = None,
        **kwargs,
    ):
        # Pass all configuration to parent, including agent_type
        super().__init__(
            agent_id=agent_id,
            orchestrator=orchestrator,
            model_config=model_config,
            stream_callback=stream_callback,
            **kwargs,
        )

    def _get_curr_messages_and_tools(self, task: TaskInput):
        """Get the current messages and tools for the agent."""
        # Get available tools (system tools + built-in tools + custom tools)
        system_tools = self._get_system_tools()
        built_in_tools = self._get_builtin_tools()
        custom_tools = self._get_registered_tools()

        # Gemini does not support built-in tools and function call at the same time.
        # If built-in tools are provided, we will switch to them in the next round.
        tool_switch = bool(built_in_tools)

        # We provide built-in tools in the first round, and then custom tools in the next round.
        if tool_switch:
            function_call_enabled = False
            available_tools = built_in_tools
        else:
            function_call_enabled = True
            available_tools = system_tools + custom_tools

        # Initialize working messages
        working_status, user_input = self._get_task_input(task)
        working_messages = self._get_task_input_messages(user_input)

        return (
            working_status,
            working_messages,
            available_tools,
            system_tools,
            custom_tools,
            built_in_tools,
            tool_switch,
            function_call_enabled,
        )

    def work_on_task(self, task: TaskInput) -> List[Dict[str, str]]:
        """
        Work on the task using the Gemini backend with conversation continuation.

        NOTE:
        Gemini's does not support built-in tools and function call at the same time.
        Therefore, we provide them interchangedly in different rounds.
        """
        curr_round = 0
        (
            working_status,
            working_messages,
            available_tools,
            system_tools,
            custom_tools,
            built_in_tools,
            tool_switch,
            function_call_enabled,
        ) = self._get_curr_messages_and_tools(task)

        # Start the task solving loop
        while curr_round < self.max_rounds and self.state.status == "working":
            try:
                # Update messages and process round
                self._update_message_notifications(working_messages, function_call_enabled)

                should_renew, new_tools = self._process_gemini_round(
                    task,
                    working_messages,
                    available_tools,
                    system_tools,
                    custom_tools,
                    built_in_tools,
                    tool_switch,
                    function_call_enabled,
                    working_status,
                )

                if should_renew:
                    # Renew conversation
                    (
                        working_status,
                        working_messages,
                        available_tools,
                        system_tools,
                        custom_tools,
                        built_in_tools,
                        tool_switch,
                        function_call_enabled,
                    ) = self._get_curr_messages_and_tools(task)
                else:
                    # Update tools if changed
                    if new_tools[0] is not None:
                        available_tools, function_call_enabled = new_tools

                curr_round += 1
                self.state.chat_round += 1

                # Check if agent voted or failed
                if self.state.status in ["voted", "failed"]:
                    break

            except Exception as e:
                self._handle_gemini_error(e, curr_round)
                curr_round += 1
                break

        return working_messages

    def _update_message_notifications(self, working_messages: List[Dict[str, str]], function_call_enabled: bool):
        """Update the last user message with tool availability notifications."""
        if working_messages[-1].get("role", "") == "user":
            if not function_call_enabled:
                working_messages[-1]["content"] += (
                    "\n\n"
                    + "Note that the `add_answer` and `vote` tools are not enabled now. Please prioritize using the built-in tools to analyze the task first."
                )
            else:
                working_messages[-1]["content"] += (
                    "\n\n" + "Note that the `add_answer` and `vote` tools are enabled now."
                )

    def _process_gemini_round(
        self,
        task,
        working_messages,
        available_tools,
        system_tools,
        custom_tools,
        built_in_tools,
        tool_switch,
        function_call_enabled,
        working_status,
    ):
        """Process a single round for Gemini agent. Returns (should_renew, (new_tools, new_enabled))."""
        # Call LLM with current conversation
        result = self.process_message(messages=working_messages, tools=available_tools)

        # Check for updates from other agents
        agents_with_update = self.check_update()
        has_update = len(agents_with_update) > 0

        # Add assistant response
        if result.text:
            working_messages.append({"role": "assistant", "content": result.text})

        # Execute function calls if any
        if result.function_calls:
            return self._handle_gemini_function_calls(
                result, agents_with_update, working_messages, built_in_tools, tool_switch
            ), (available_tools, function_call_enabled)
        else:
            return self._handle_gemini_no_function_calls(
                has_update, working_messages, working_status, system_tools, custom_tools, tool_switch
            )

    def _handle_gemini_function_calls(self, result, agents_with_update, working_messages, built_in_tools, tool_switch):
        """Handle function calls for Gemini agent."""
        # Deduplicate function calls by their name
        result.function_calls = self.deduplicate_function_calls(result.function_calls)
        function_outputs, successful_called = self._execute_function_calls(
            result.function_calls, invalid_vote_options=agents_with_update
        )

        # Check if conversation needs renewal
        for function_call, successful_call in zip(result.function_calls, successful_called):
            if successful_call and function_call.get("name") in ["add_answer", "vote"]:
                return True  # Renew conversation

        # Add function call results to conversation
        for function_call, function_output in zip(result.function_calls, function_outputs):
            working_messages.extend([function_call, function_output])

        # Switch to built-in tools if needed
        if tool_switch:
            print(f"🔄 Agent {self.agent_id} (Gemini) switching to built-in tools in the next round")

        return False  # Continue current conversation

    def _handle_gemini_no_function_calls(
        self, has_update, working_messages, working_status, system_tools, custom_tools, tool_switch
    ):
        """Handle case when no function calls were made for Gemini agent."""
        if self.state.status == "voted":
            return False, (None, None)  # Agent has voted, will exit loop

        if has_update and working_status != "initial":
            return True, (None, None)  # Renew conversation due to updates
        else:
            # Prompt for tool call
            working_messages.append(
                {
                    "role": "user",
                    "content": "Finish your work above by making a tool call of `vote` or `add_answer`. Make sure you actually call the tool.",
                }
            )

            # Switch to custom tools in the next round
            if tool_switch:
                new_tools = system_tools + custom_tools
                print(f"🔄 Agent {self.agent_id} (Gemini) switching to custom tools in the next round")
                return False, (new_tools, True)

            return False, (None, None)

    def _handle_gemini_error(self, error: Exception, curr_round: int):
        """Handle Gemini agent errors during task processing."""
        print(f"❌ Agent {self.agent_id} error in round {self.state.chat_round}: {error}")
        if self.orchestrator:
            self.orchestrator.mark_agent_failed(self.agent_id, str(error))
        self.state.chat_round += 1


class OpenRouterMassAgent(OpenAIMassAgent):
    """MassAgent wrapper for OpenRouter API models (e.g., DeepSeek R1)."""

    def __init__(
        self,
        agent_id: int,
        orchestrator=None,
        model_config: Optional[ModelConfig] = None,
        stream_callback: Optional[Callable] = None,
        **kwargs,
    ):
        # Set OpenRouter base URL
        os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"

        # Use OpenRouter API key
        api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_KEY")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key

        # Pass all configuration to parent
        super().__init__(
            agent_id=agent_id,
            orchestrator=orchestrator,
            model_config=model_config,
            stream_callback=stream_callback,
            **kwargs,
        )


def create_agent(
    agent_type: str,
    agent_id: int,
    orchestrator=None,
    model_config: Optional[ModelConfig] = None,
    **kwargs,
) -> MassAgent:
    """
    Factory function to create agents of different types.

    Args:
        agent_type: Type of agent ("openai", "gemini", "grok", "openrouter")
        agent_id: Unique identifier for the agent
        orchestrator: Reference to the MassOrchestrator
        model_config: Model configuration
        **kwargs: Additional arguments

    Returns:
        MassAgent instance of the specified type
    """
    agent_classes = {
        "openai": OpenAIMassAgent,
        "gemini": GeminiMassAgent,
        "grok": GrokMassAgent,
        "openrouter": OpenRouterMassAgent,
    }

    if agent_type not in agent_classes:
        raise ValueError(f"Unknown agent type: {agent_type}. Available types: {list(agent_classes.keys())}")

    return agent_classes[agent_type](
        agent_id=agent_id,
        orchestrator=orchestrator,
        model_config=model_config,
        **kwargs,
    )
