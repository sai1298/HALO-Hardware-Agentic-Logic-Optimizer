# -*- coding: utf-8 -*-
import subprocess
from typing import Optional

class BambuRunner:
    """
    A utility class to interface with the Bambu High-Level Synthesis (HLS) tool.
    Handles hardware synthesis and simulation via subprocess calls.
    """

    @staticmethod
    def run_bambu_synthesis(
        c_file_name: str,
        top_fname: str,
        generate_tb: str,
        working_directory: str
    ) -> Optional[str]:
        """
        Executes the Bambu synthesis process for a given C file.

        Args:
            c_file_name: The source C file to synthesize.
            top_fname: The name of the top-level function.
            generate_tb: Path or flag for testbench generation.
            working_directory: The directory where the command should execute.

        Returns:
            An error report string if synthesis fails, otherwise None.
        """
        command = [
          "bambu",
          c_file_name,
          f"--top-fname={top_fname}",
          "--device-name=xc7z020-1clg484-VVD",
          "--clock-period=5",
          f"--generate-tb={generate_tb}",
          "-v4",
          "-I../../common"
        ]
        try:
            # We still capture output, but we don't print it unless an exception occurs
            subprocess.run(command,cwd=working_directory,
                          capture_output=True, text=True, check=True)
            return None

        except subprocess.CalledProcessError as e:
            # Construct the error report
            error_report = f"Standard Error:\n{e.stderr}\nStandard Output:\n{e.stdout}"
            # Return the error for LangGraph/LLM processing
            return error_report

    @staticmethod
    def run_bambu_simulation(
        tb_file: str,
        top_fname: str,
        working_dir: str,
        source_file: str = "aes.c"
    ) -> Optional[str]:
        """
        Runs a simulation of the synthesized hardware using Bambu.

        Args:
            tb_file: Path to the testbench file.
            top_fname: The name of the top-level function.
            working_dir: Execution directory.
            source_file: The source C file used for simulation.

        Returns:
            The full simulation output string on success, or None on failure.
        """
        command = [
            "bambu",
            "--generate-interface=INFER",
            f"--generate-tb={tb_file}",
            source_file,
            f"--top-fname={top_fname}",
            "--simulate",
            "-v1",
            "-I../../common"
        ]

        try:
            result = subprocess.run(
                command,
                cwd=working_dir,
                check=True,
                text=True,
                stdout=subprocess.PIPE,     # Capture success logs
                stderr=subprocess.STDOUT    # Merge stderr into stdout for unified logging
            )

            print(result.stdout)
            return result.stdout

        except subprocess.CalledProcessError as e:
            print(f"\nCommand failed with exit code {e.returncode}")
            print(f"Error Output:\n{e.output}")
            return None

        except FileNotFoundError:
            print(
                f"\nError: 'bambu' executable not found in PATH or "
                f"directory '{working_dir}' does not exist."
            )
            return None





google_api_key = 'AIzaSyDYH_pAEc6SNrtgzfST0ZV_Sc5TWrxw0QI'

from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize the model
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    max_tokens=65536,
    api_key=google_api_key
)

llm = gemini_llm

## adding the state to the langgraph
from typing import TypedDict, Optional

class GraphState(TypedDict):
    file_path: str
    code: str
    pragma_type: str
    modified_code: str
    error: Optional[str]
    modified_file_path: str
    retry_count: int
    max_retries: int
    working_dir: str
    tb_file: str
    top_fname: str

## load the c code
def load_file_node(state: GraphState):
    path = state.get("file_path", "")

    if not os.path.exists(path):
        return {"error": f"File not found at: {path}"}

    try:
        with open(path, 'r') as f:
            content = f.read()
        return {"code": content, "error": None}
    except Exception as e:
        return {"error": f"Failed to read file: {str(e)}"}

system_prompt = """Role & Objective
You are an expert Hardware Design Engineer specializing in High-Level Synthesis (HLS) using the PandA Bambu compiler. Your task is to take standard C code and inject appropriate #pragma HLS directives to optimize the hardware generation (e.g., unrolling loops, inlining functions, and defining memory interfaces).
CRITICAL COMPILER RULES (STRICT ADHERENCE REQUIRED)
Bambu uses a very strict Clang-based front-end. Standard C parsing rules apply to pragmas. If you violate these rules, the compiler will fail with "Front-end compiler returns an error". You MUST follow these syntax constraints
Loop Unrolling Placement: Use #pragma HLS unroll. It MUST be placed exactly one line above the loop keyword (for, while, or do). Do not place any statements or variable declarations between the pragma and the loop.
The "Label" Rule (Extremely Important):
If a loop has a named C label (e.g., my_loop:), the label is technically a C statement. Therefore, the label MUST go before the pragma.
INCORRECT (Will crash):
#pragma HLS unroll
my_loop: for(int i=0; ...)
CORRECT:
my_loop:
#pragma HLS unroll
for(int i=0; ...)
No Pipelining Pragmas:
DO NOT use #pragma HLS pipeline. Bambu handles pipelining natively or via command-line arguments in this environment. Using inline pipeline pragmas will cause an "unsupported pragma" compilation error.
Function Inlining:
For small helper functions or mathematical operations, place #pragma HLS inline immediately inside the opening brace of the function definition.
Top-Level Interfaces:
For the top-level function, map pointer or array arguments to memory interfaces using:
#pragma HLS interface mode=m_axi port=<arg_name> offset=direct
Place these immediately inside the opening brace of the top-level function.
###########
Output Format
Return ONLY the complete, compilable C code. Do not include markdown formatting (like ```c) unless requested by the user, and do not provide explanations unless specifically asked. The code must be ready to be passed directly into a .c file for the Bambu compiler. create a small syntax error in output code.
"""

# node to add pragram to c code  and write it to the file
from langchain_core.messages import SystemMessage, HumanMessage

def add_pragma_llm_node(state: GraphState):
    code = state.get("code", "")
    # Define the instruction
    file_path = state.get("file_path", "")
    output_path = file_path.rsplit(".", 1)[0] + "_optimised." + file_path.rsplit(".", 1)[1]

    human_prompt = f"Add '#pragma to the following code:\n\n{code}"

    try:
        # Call the LLM
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ])
        modified_code = str()

        if response is not None and response.content:
            modified_code = response.content.replace("```c", "").replace("```", "").strip()
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(modified_code)
            except IOError as e:
                return {"error": f"Failed to write to file: {str(e)}"}

        # Simple validation: Did the LLM actually return code?
        if not modified_code:
            return {"error": "LLM returned an empty string."}

        return {"modified_code": modified_code,"modified_file_path":output_path,"error": None}

    except Exception as e:
        return {"error": f"LLM Call failed: {str(e)}"}

agent_prompt ='''
You are an autonomous expert Hardware Design Engineer specializing in High-Level Synthesis (HLS) using the PandA Bambu compiler. Your objective is to take standard C code, inject the correct #pragma HLS directives, and ensure successful synthesis through an iterative testing loop.

CRITICAL COMPILER RULES (STRICT ADHERENCE REQUIRED):
1. Loop Unrolling: Use `#pragma HLS unroll`. It MUST be placed exactly one line above the loop keyword (for, while, do). Do not place any statements or declarations between the pragma and the loop.
2. The "Label" Rule: If a loop has a named C label, the label MUST go before the pragma (e.g., `my_loop:\n#pragma HLS unroll\nfor(int i=0; ...)`).
3. No Pipelining: DO NOT use `#pragma HLS pipeline`. Bambu handles this natively; using it will cause an "unsupported pragma" error.
4. Function Inlining: Place `#pragma HLS inline` immediately inside the opening brace of any small helper functions or mathematical operations.
5. Top-Level Interfaces: Map pointer or array arguments to memory interfaces using `#pragma HLS interface mode=m_axi port=<arg_name> offset=direct`. Place these immediately inside the opening brace of the top-level function.

WORKFLOW & EXECUTION INSTRUCTIONS:
1. Initial Generation: Generate the complete, correct C code with the required pragmas.
2. Strict Formatting: Return ONLY the raw C code. Do not use markdown formatting (like ```c), and do not provide explanations. The output must be ready to pass directly into a .c file.
3. Synthesis Testing: Invoke the `run_synthesis_tool` to test your generated C code.
4. Iterative Debugging: If the tool returns an error, carefully read the error message, fix the C code (maintaining all strict HLS rules), and call the `run_synthesis_tool` again.
5. Completion condition: Continue this debug loop until the tool returns "Success". Stop once synthesis is successfully achieved.

'''

import os
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent

def synthesis_agent_node(state: GraphState):
    """An agent node that runs synthesis and automatically fixes code if it fails."""

    current_code = state.get("modified_code", "")
    output_path = state.get("modified_file_path", "optimised.c")
    c_file_name = os.path.basename(output_path)
    max_retries = state.get("max_retries", 3)

    # 1. Define the Tool for the Agent
    @tool
    def run_synthesis_tool(updated_code: str) -> str:
        """
        Use this tool to compile and synthesize the C code.
        Pass the COMPLETE C code as a string.
        Returns 'Success' if it works, or the compiler error message if it fails.
        """
        # Save the agent's code attempt to the file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(updated_code)

        print(f"--- Agent attempting synthesis on {c_file_name} ---")

        # Run Bambu (using your existing function)
        error_output = BambuRunner.run_bambu_synthesis(
            c_file_name=c_file_name,
            top_fname=state.get("top_fname", ""),
            generate_tb=state.get("tb_file", ""),
            working_directory=state.get("working_dir", "")
        )

        if error_output:
            return f"Synthesis Failed. Analyze this error and try again:\n{error_output}"

        return "Success"

    # 2. Define the Agent's behavior
    system_prompt = agent_prompt

    # Create the ReAct agent
    agent = create_react_agent(llm, tools=[run_synthesis_tool], prompt=system_prompt)

    # Limit how many times the agent can loop internally (tool call + LLM response = 2 steps per retry)
    config = {"recursion_limit": (max_retries * 2) + 2}
    human_prompt = f"Please synthesize and fix this code if necessary without modify th core logic:\n\n{current_code}"

    try:
        # Run the agent loop
        response = agent.invoke({"messages": [HumanMessage(content=human_prompt)]}, config=config)

        # Once the agent completes successfully, the final correct code is already written to the file by the tool.
        # We just need to load it back into the state.
        with open(output_path, "r", encoding="utf-8") as f:
            final_code = f.read()

        # Check if the final message indicates failure or if we hit the recursion limit
        last_message = response["messages"][-1].content
        if "Failed" in last_message or "error" in last_message.lower():
             return {"error": "Agent failed to synthesize code within the retry limit.", "modified_code": final_code}

        return {"error": None, "modified_code": final_code}

    except Exception as e:
        # Catches recursion limit errors (GraphRecursionError) if it loops too many times
        return {"error": f"Synthesis agent stopped: {str(e)}"}

def run_bambu_simulation_node(state: GraphState):
    """Executes the simulation to verify the synthesized RTL logic."""
    print("--- Step 4: Running Simulation ---")
    try:
        BambuRunner.run_bambu_simulation(
        tb_file= state.get("tb_file", ""),
        top_fname= state.get("top_fname", ""),
        working_dir= state.get("working_dir", ""),
        source_file = state.get("modified_file_path","")
        )
        print("Simulation Successful!")
        return {"error": None}

    except subprocess.CalledProcessError as e:
        print(f"Simulation Failed: {e.stderr}")
        return {"error": f"Simulation Error: {e.stderr}"}

from langgraph.graph import StateGraph, END

def check_agent_success(state: GraphState) -> str:
    """Simple router to check if the agent succeeded before running simulation."""
    if state.get("error"):
        print(f"Workflow halting: {state['error']}")
        return "failure"
    return "success"

workflow = StateGraph(GraphState)

# Add nodes
workflow.add_node("load_file", load_file_node)
workflow.add_node("add_pragma", add_pragma_llm_node)
workflow.add_node("synthesis_agent", synthesis_agent_node) # Replacing run & retry nodes
workflow.add_node("run_simulation", run_bambu_simulation_node)

# Define the sequence
workflow.set_entry_point("load_file")
workflow.add_edge("load_file", "add_pragma")
workflow.add_edge("add_pragma", "synthesis_agent")
workflow.add_edge("synthesis_agent", "run_simulation")

# Route based on the agent's ultimate success/failure
workflow.add_conditional_edges(
    "synthesis_agent",
    check_agent_success,
    {
        "success": "run_simulation",
        "failure": END
    }
)

workflow.add_edge("run_simulation", END)

app = workflow.compile()

from IPython.display import Image, display

try:
    # Generate the image bytes
  image_data = app.get_graph().draw_mermaid_png()

  # Save to a file
  with open("/content/HLS/graph_visualization.png", "wb") as f:
      f.write(image_data)

  print("Image saved as graph_visualization.png")
except Exception:
    # This requires pygraphviz or similar; falls back to text if unavailable
    print("Graph compiled successfully. Visualization requires extra dependencies.")

input_msg = {
    "file_path": "/content/HLS/MachSuite/aes/aes/aes.c",
    "pragma_type": "HLS",
    "retry_count": 0,
    "max_retries": 3,
    "working_dir": "/content/HLS/MachSuite/aes/aes",
    "tb_file": "aes_test.c",
    "top_fname": "aes256_encrypt_ecb"
}

for chunk in app.stream(input_msg):
    print(chunk)

