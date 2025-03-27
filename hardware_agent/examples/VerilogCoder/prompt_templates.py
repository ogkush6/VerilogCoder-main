#
# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# Author : Chia-Tung (Mark) Ho, NVIDIA
#

VERILOG_PLAN_RETRIEVE_PROMPT_TEMPLATE="""
You are a top-tier Verilog expert with experience in retrieving required information for the following plan using retrieve_additional_plan_information_tool. 
[Module Description]:
{Module}

[Current Plan Description]: 
```
{CurrentPlan}
```

Let's think step by step. 
1. Set BFS_retrival_level=2.
2. Use retrieve_additional_plan_information_tool to retrieve the required information. The rules for covering the plan are below.
   - have the signal mentioned in the plan
   - Must have the signal example if there are any related to the plan
3. Increase the BFS_retrival_level by 1 and repeat the step 2. BFS_retrival_level should not exceed 10. 
   - If the plan is well covered by the retrieved information or no more retrieved information available, go to Step 4.
4. Compile the node names and descriptions which covers the plan from the BFS result.
   - You must remove the signal which is not mentioned in the plan. Make the related information short and be able to cover the plan need.
   - Must include the signal example (Type: SignalExample) if the signal is mentioned in the plan.

Return the Plan and retrieved related information from retrieve_additional_plan_information_tool.
If there is no retrieved related information needed for the plan, just return the Plan. 
The return format is below.
```
{CurrentPlan}

Retrieved Related Information:
Info 1
Info 2
...
```
After the return format, reply TERMINATE to end.
"""

Verilog_Plan_Template_Prompt = """You are a Verilog RTL designer that can break down complicated implementation into subtasks implementation plans.

[Example Begin]
{VerilogExamples}
[Example End]

[Target Problem]
### Problem 

{ModulePrompt}

[Instruction]
Let's think step by step. 
Based on the Problem description, set up a sequential implementation plans. Each subtask should focus on implement only one signal at a time. 
Extract the corresponding source contexts in the [Target Problem] section of each subtask into the 'source' field. 

- If the problem is related to sequential circuit waveform, analyze the waveform of clk and signals to identify flip-flop and latch first before complete the plans.
  If the signal changes when clock is active for more than a time point, it is a Latch. 
- You can use sequential_flipflop_latch_identify_tool example only when there is a simulation waveform provided in the prompt. Do not generate your own waveform to use the tool.

- If the 'source' is a part of K-map, you must extract the corresponding row or column. Below is an example of extracting a row or a column in K-map.
[K-map Table Example]:
             a,b      
  c,d  0,0 0,1 1,1 1,0 
  0,0 | 0 | 0 | 0 | 1 |
  0,1 | 1 | 0 | 0 | 0 |
  1,1 | d | 1 | 0 | 1 |
  1,0 | 0 | 0 | 0 | 0 |
  
  [Extract Row (c,d) = (1,1)]
  ```
  The output row is below
             a,b
  c,d  0,0 0,1 1,1 1,0
  1,1 | d | 1 | 0 | 1 |
  ```
  
  [Extract Column (a,b) = (1,0)]
  ```
  The output column is below. 
       a,b
  c,d  1,0  
  0,0 | 1 |
  0,1 | 0 | 
  1,1 | 1 | 
  1,0 | 0 |
  ```
   
[K-map Table Example End]
 
The task id number indicates the sequential orders. Return the subtasks in json format as below. 
```json
{SubtaskExample}
```

[Rules]
Make sure the task plans satisfy the following rules! Do not make the plans that violate the following rules!!!
- Make a plan to define the module with its input and output first.
- Do not plan the implementation of logic or signal from the input ports.
- There is test bench to test the functional correctness. Do not plan generating testbench to test the generated verilog code. 
- Don't make a plan only with clock or control signals. The clock or control signals should be planned with register or wire signal.
- Don't make a plan on implementing the signal or next state logics which are not related to the module outputs.
- For module related to Finite State Machine (FSM), try to determine the number of states first and then make the plan to implement FSM.
- For module related to Finite State Machine or Moore State Machine, if the state or current_state is a input port signal of the module, You must Do Not implement the state flip-flops for state transition as the example below in TopModule. 
  [State flip-flops for Transition Block Example]
  always@(*) begin
    ...
    state <= next_state;
    ...
  end
  [State flip-flops for Transition Block Example End]
"""

SUBTASK_FORMAT_EXAMPLE="""{
    "subtasks": [
                    {
                        "id": "1",
                        "content": "task description 1",
                        "source": "source 1"
                    },
                    {
                        "id": "2",
                        "content": "task description 2",
                        "source": "source 2"
                    },
                    {
                        "id": "3",
                        "content": "task description 3",
                        "source": "source 3"
                    },
                    ...
                ]
}
"""

Verilog_signal_extraction_hint = """
Extract the signal and its description, state transition description, and signal example contents in the json format.
The return format need to follow ```json and ``` format. 
```json
{
  "signal": ["<signal1 name>: <signal1 description>", "<signal2 name>: <signal2 description>", ...], # list of strings
  "state_transitions_description": [<state_transition_line1>, <state_transistion_line2>, ...], # list of strings
  "signal_examples": [<text1>, <text2>, ...], # list of strings
}
```

[Rules]:
- You must extract the signals and all signal examples in the description!
- Do not implement the verilog code. Do not change the original description and text.
- Do not change the state_transition format when extracting to 'state_transitions_description'.
- For simulation waveform, if it is a sequential circuit, be attention to the output and input signal transitions at clock edge (0 -> 1 posedge, or 1-> 0 negedge for flip-flops), or during active high period of clock for latch. 
- If the state_transition is represented as K-map table, you need to extract the row or column values with their corresponding row or column signals.
- Do not add signal examples if there is no examples in the module description.

[Hint]
For K-map Table below, you should read it in row based or column based based on the module description.
[K-map Table Example]:
             a,b      
  c,d  0,0 0,1 1,1 1,0 
  0,0 | 0 | 0 | 0 | 1 |
  0,1 | 1 | 0 | 0 | 0 |
  1,1 | d | 1 | 0 | 1 |
  1,0 | 0 | 0 | 0 | 0 |
  
  [Extract Row (c,d) = (1,1)]
  ```
  The output row is below
             a,b
  c,d  0,0 0,1 1,1 1,0
  1,1 | d | 1 | 0 | 1 |
  ```
  
  [Extract Column (a,b) = (1,0)]
  ```
  The output column is below. 
       a,b
  c,d  1,0  
  0,0 | 1 |
  0,1 | 0 | 
  1,1 | 1 | 
  1,0 | 0 |
  ```
   
[K-map Table Example End]
"""

Verilog_Signal_Extract_Template_Prompt = """You are a Verilog RTL designer that identify the signals, state transition description, and signal example contents.

[Module Description]
{ModulePrompt}

[Instruction]
{SignalExtractRule}
"""

Verilog_Subtask_Template_Prompt = """You are a Verilog RTL designer that only writes code using correct Verilog syntax based on the task definition.

[Example Begin]
{VerilogExamples}
[Example End]

[Module Description]
{ModulePrompt}

[Previous Module Implementation]
```verilog
{PreviousTaskOutput}
```

[Current SubTask]
{Task}

[Hints]:
- For implementing kmap, you need to think step by step. Find the inputs corresponding to output=1, 0, and don't-care for each case. Categorized them and find if there are any combinations that can be simplify.  

[Rules]:
- Only write the verilog code for the [Current SubTask]. Don't generate code without defined in the [Current SubTask].
- Don't change or modify the code in [Previous Module Implementation].
- Return the written verilog log code with Previous Module Implementation. 
- Declare all ports and signals as logic.
- Don't use state_t to define the parameter. Use `localparam` or Use 'reg' or 'logic' for signals as registers or Flip-Flops.
- Don't generate duplicated signal assignments or blocks.
- Define the parameters or signals first before using them.
- Not all the sequential logic need to be reset to 0 when reset is asserted.    
- for combinational logic, you can use wire assign (i.e., assign wire = a ? 1:0;) or always @(*).
- for combinational logic with an always block do not explicitly specify the sensitivity list; instead use always @(*).
- For 'if' block, you must use begin and end as below.
  [if example]
  if (done) begin
    a = b;
    n = q;
  end
  [if example end]
"""

# Other ICL rules
#  - for combinational logic with an always block do not explicitly specify
#    the sensitivity list; instead use always @(*)
#
#  - all sized numeric constants must have a size greater than zero
#    (e.g, 0'b0 is not a valid expression)
#
#  - an always block must read at least one signal otherwise it will never
#    be executed; use an assign statement instead of an always block in
#    situations where there is no need to read any signals
#
#  - if the module uses a synchronous reset signal, this means the reset
#    signal is sampled with respect to the clock. When implementing a
#    synchronous reset signal, do not include posedge reset in the
#    sensitivity list of any sequential always block.

Verilog_Subtask_Prompt = """You are a Verilog RTL designer that only writes code using correct Verilog syntax and verify the functionality. 
You need to run the verilog_simulation_tool to make sure the functional correctness before TERMINATE.

[Target Module Description]
### Problem 
{ModulePrompt}

### Completed Verilog Module
```verilog
{PreviousTaskOutput}
```


[Instructions]:
1. Use the verilog_simulation_tool to verify the syntax and functional correctness of the Completed Verilog Module.
2. Use the waveform_trace_tool to trace the waveform of functional incorrect signals by inputting the verilog_simulation_tool result.
3. Debug the waveform and verilog source code and find out the signals need to be corrected.
4. Repeat above steps until pass the syntax and functional check.

[Constraints]:
- Do not use typedef enum in the verilog code.
- There is test bench to test the functional correctness. You don't need to generate testbench to test the generated verilog code.
- Do not use $display or $finish in the module implementation.
- You can not modify the testbench.
- Declare all ports as logic; use wire or reg for signals inside the block.
- Don't use state_t. Use 'reg' or 'logic' for signals as registers or Flip-Flops.
- for combinational logic, you can use wire assign or always @(*).
- for combinational logic with an always block do not explicitly specify the sensitivity list; instead use always @(*)
- Don't generate duplicated signal assignments or blocks.
"""

CompletedModule="""
module TopModule (
    input  logic clk,
    input  logic reset,
    input  logic s,
    input  logic w,
    output logic z
);

    // State definitions
    localparam STATE_A = 2'b00;
    localparam STATE_B = 2'b01;
    localparam STATE_Z = 2'b10;

    // State register
    logic [1:0] state;
    logic [1:0] state_next;

    // Counter for state B
    logic [1:0] counter;
    logic [1:0] count_ones;

    // Sequential logic for state transitions
    always @(posedge clk) begin
        if (reset) begin
            state <= STATE_A;
            counter <= 0;
            count_ones <= 0;
        end else begin
            state <= state_next;
            if (state == STATE_B) begin
                counter <= counter + 1;
                count_ones <= count_ones + w;
            end else begin
                counter <= 0;
                count_ones <= 0;
            end
        end
    end

    // Next state logic
    always @(*) begin
        state_next = state; // Default to hold current state
        case (state)
            STATE_A: begin
                if (s == 1)
                    state_next = STATE_B;
            end
            STATE_B: begin
                if (counter == 2) begin // After three cycles in STATE_B
                    if (count_ones == 2)
                        state_next = STATE_Z;
                    else
                        state_next = STATE_A;
                end
            end
            STATE_Z: begin
                state_next = STATE_A; // Go back to STATE_A after outputting in STATE_Z
            end
        endcase
    end

    // Output logic
    always @(*) begin
        z = (state == STATE_Z);
    end

endmodule
"""

Verilog_With_Internal_Planner_Prompt = """You are a Verilog RTL designer that only writes code using correct Verilog syntax and verify the functionality. You need to run the simulator to check whether the function is correct!

[Example Begins]
### Problem

I would like you to implement a module named TopModule with the following
interface. All input and output ports are one bit unless otherwise
specified.

 - input  clk
 - input  reset
 - input  in_ (8 bits)
 - output out (8 bits)

The module should implement an 8-bit registered incrementer. The 8-bit
input is first registered and then incremented by one on the next cycle.

Assume all sequential logic is triggered on the positive edge of the
clock. The reset input is active high synchronous and should reset the
output to zero.

### Solution

module TopModule
(
  input  logic       clk,
  input  logic       reset,
  input  logic [7:0] in_,
  output logic [7:0] out
);

  // Sequential logic

  logic [7:0] reg_out;

  always @( posedge clk ) begin
    if ( reset )
      reg_out <= 0;
    else
      reg_out <= in_;
  end

  // Combinational logic

  logic [7:0] temp_wire;

  always @(*) begin
    temp_wire = reg_out + 1;
  end

  // Structural connections

  assign out = temp_wire;

endmodule

### Problem

I would like you to implement a module named TopModule with the following
interface. All input and output ports are one bit unless otherwise
specified.

 - input  clk
 - input  reset
 - input  in_
 - output out

The module should implement a finite-state machine that takes as input a
serial bit stream and outputs a one whenever the bit stream contains two
consecutive one's. The output is one on the cycle _after_ there are two
consecutive one's.

Assume all sequential logic is triggered on the positive edge of the
clock. The reset input is active high synchronous and should reset the
finite-state machine to an appropriate initial state.

### Solution

module TopModule
(
  input  logic clk,
  input  logic reset,
  input  logic in_,
  output logic out
);

  // State enum

  localparam STATE_A = 2'b00;
  localparam STATE_B = 2'b01;
  localparam STATE_C = 2'b10;

  // State register

  logic [1:0] state;
  logic [1:0] state_next;

  always @(posedge clk) begin
    if ( reset )
      state <= STATE_A;
    else
      state <= state_next;
  end

  // Next state combinational logic

  always @(*) begin
    state_next = state;
    case ( state )
      STATE_A: state_next = ( in_ ) ? STATE_B : STATE_A;
      STATE_B: state_next = ( in_ ) ? STATE_C : STATE_A;
      STATE_C: state_next = ( in_ ) ? STATE_C : STATE_A;
    endcase
  end

  // Output combinational logic

  always @(*) begin
    out = 1'b0;
    case ( state )
      STATE_A: out = 1'b0;
      STATE_B: out = 1'b0;
      STATE_C: out = 1'b1;
    endcase
  end

endmodule
[Example End]

[Target Problem]
### Problem 

{ProblemPrompt}

[Hints]:
1. Make a plan to construct the state machine transition table. In the plan, you must explain the state transitions with bulletins.
2. Implement verilog code steps by steps.
3. Use the verilog_simulation_tool to verify the syntax and functional correctness of the generated code.
4. Use the waveform_trace_tool to trace the waveform and partial verilog code of functional incorrect signals.
5. Debug the waveform and verilog source code and find out the signals need to be corrected.
6. If the code is still not correct, use the recall_spec_and_generated_verilog_code_tool to recall the module spec and implemented verilog module for further analysis and debugging.
7. Repeat above steps until pass the syntax and functional check.

[Constraints]:
Do not use typedef enum in the verilog code.
There is test bench to test the functional correctness. You don't need to generate testbench to test the generated verilog code.
You can not modify the testbench.
"""
