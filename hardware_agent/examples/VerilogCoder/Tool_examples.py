#
# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# Author : Chia-Tung (Mark) Ho, NVIDIA
#

ToolExamplePrefix="""

### Calling Tool Examples ###
You need to follow the tool calling format as shown in the example below. You must maintain the verilog code structure (i.e., line and spaceing) for syntax check and simulation tools.

[Tool Examples]

Follow the Action and Argument properly, the user needs to parse these so the format needs to be the same. Call functions directly by their names.
Directly say the function name after the "Call", do not use any prefix. Do not call functions.function_name. Just function_name will do
Format:

Action: Call function_name tool to ....
Action Input: ```{"dictionary containing input keys and values for the function_name"}```

Make sure you have ``` and ``` enclose the Action Input.
"""

ToolExampleEnd="""
[Tool Examples End]
"""

RetrievalToolExamples="""
[Retrieval tool Example]: Retrieve additional plan information
Action: Call retrieve_additional_plan_information_tool tool to retrieve the information for the plan
Action Input: ```{"current_plan": "Implement the module", "BFS_retrival_level": 2}```

"""

SyntaxCheckerToolExamples_3_1="""
[Syntax check tool Example1]: Check Verilog syntax of generated verilog module inside the ```verilog and ``` code block. Do not include ```verilog and ``` . 
```verilog
module TopModule
(
    input logic a,
    output logic b
);
    assign b = ~a;
endmodule
``` 

Action: Call verilog_syntax_check_tool tool to check the syntax of generated verilog code inside the ```verilog and ``` code block. Do not include ```verilog and ``` .
Action Input: ```{"completed_verilog": "module TopModule
(
    input logic a,
    output logic b
);
    assign b = ~a;
endmodule"
}```

[Syntax check tool Example2]: Check Verilog syntax of generated verilog module inside the ```verilog and ``` code block. Do not include ```verilog and ``` .
```verilog
module TopModule
(
    input logic a,
    input logic b,
    output logic c
);
    assign c = a ^ b;
    
endmodule
``` 

Action: Call verilog_syntax_check_tool tool to check the syntax of generated verilog code inside the ```verilog and ``` code block. Do not include ```verilog and ``` .
Action Input: ```{"completed_verilog": "module TopModule
(
    input logic a,
    input logic b,
    output logic c
);
    assign c = a ^ b;
endmodule"
}```

"""

SimulatorToolExamples_3_1="""
[verilog_simulation_tool Example1]: Check the syntax and functional correctness of generated verilog module code inside the ```verilog and ``` code block. Do not include ```verilog and ``` .
```verilog
module TopModule
(
    input logic a,
    output logic b
);
    assign b = ~a;
endmodule
``` 

Action: Call verilog_simulation_tool tool to check the syntax and functionality of generated verilog module code inside the ```verilog and ``` code block. Do not include ```verilog and ``` .
Action Input: ```{"completed_verilog": "module TopModule
(    
    input logic a,
    output logic b
);
    assign b = ~a;
endmodule"
}```

[verilog_simulation_tool Example2]: Check the syntax and functional correctness of generated verilog module code inside the ```verilog and ``` code block. Do not include ```verilog and ``` .
```verilog
module TopModule
(
    input logic a,
    input logic b,
    output logic c
);
    assign c = a ^ b;
    
endmodule
``` 

Action: Call verilog_simulation_tool tool to check the syntax and functionality of generated verilog module code inside the ```verilog and ``` code block. Do not include ```verilog and ``` .
Action Input: ```{"completed_verilog": "module TopModule
(
    input logic a,
    input logic b,
    output logic c
);
    assign c = a ^ b;
endmodule"
}```

"""

SyntaxCheckerToolExamples="""
[Syntax check tool Example1]: Check Verilog syntax of generated verilog module inside the ```verilog and ``` code block. Do not include ```verilog and ``` .
```verilog
module TopModule
(
    input logic a,
    output logic b
);
    assign b = ~a;
endmodule
``` 

Action: Call verilog_syntax_check_tool tool to check the syntax of generated verilog code inside the ```verilog and ``` code block. Do not include ```verilog and ``` .
Action Input: ```{"completed_verilog": "module TopModule\n(\n    input logic a,\n    output logic b\n);\n    assign b = ~a;\nendmodule"}```

[Syntax check tool Example2]: Check Verilog syntax of generated verilog module inside the ```verilog and ``` code block. Do not include ```verilog and ``` .
```verilog
module TopModule
(
    input logic a,
    input logic b,
    output logic c
);
    assign c = a ^ b;
    
endmodule
``` 

Action: Call verilog_syntax_check_tool tool to check the syntax of generated verilog code inside the ```verilog and ``` code block. Do not include ```verilog and ``` .
Action Input: ```{"completed_verilog": "module TopModule\n(\n    input logic a,\n    input logic b,\n    output logic c\n);\n    assign c = a ^ b;\nendmodule"}```

"""

SimulatorToolExamples="""
[Verilog simulation tool Example1]: Check the syntax and functional correctness of generated verilog module inside the ```verilog and ``` code block. Do not include ```verilog and ``` .
```verilog
module TopModule
(
    input logic a,
    output logic b
);
    assign b = ~a;
endmodule
``` 

Action: Call verilog_simulation_tool tool to check the syntax and functionality of generated verilog code inside the ```verilog and ``` code block. Do not include ```verilog and ``` .
Action Input: ```{"completed_verilog": "module TopModule\n(\n    input logic a,\n    output logic b\n);\n    assign b = ~a;\nendmodule"}```

[Verilog simulation tool Example2]: Check the syntax and functional correctness of generated verilog module inside the ```verilog and ``` code block. Do not include ```verilog and ``` .
```verilog
module TopModule
(
    input logic a,
    input logic b,
    output logic c
);
    assign c = a ^ b;
    
endmodule
``` 

Action: Call verilog_syntax_check_tool tool to check the syntax of generated verilog code inside the ```verilog and ``` code block. Do not include ```verilog and ``` .
Action Input: ```{"completed_verilog": "module TopModule\n(\n    input logic a,\n    input logic b,\n    output logic c\n);\n    assign c = a ^ b;\nendmodule"}```
"""

WaveformTraceToolExamples="""
[waveform_trace_tool Example 1]: Use the signal waveform to debug for functional error. You must do not change the response! 
*** Response from verilog_simulation_tool ***
[Compiled Success]
[Function Check Failed]
VCD info: dumpfile wave.vcd opened for output.
VCD warning: $dumpvars: Package ($unit) is not dumpable with VCD.
/home/scratch.chiatungh_nvresearch/hardware-agent-marco/verilog_tool_tmp1//test.sv:30: $finish called at 102 (1ps)
Hint: Output 'one' has 3 mismatches.
Hint: Total mismatched samples is 3 out of 20 samples

Simulation finished at 102 ps
Mismatches: 3 in 20 samples
*********************************************

Action: Call waveform_trace_tool tool to debug the functional error from the simulation tool response of generated verilog code
Action Input: ```{
"function_check_output": "[Compiled Success]
[Function Check Failed]
VCD info: dumpfile wave.vcd opened for output.
VCD warning: $dumpvars: Package ($unit) is not dumpable with VCD.
/home/scratch.chiatungh_nvresearch/hardware-agent-marco/verilog_tool_tmp1//test.sv:30: $finish called at 102 (1ps)
Hint: Output 'one' has 3 mismatches.
Hint: Total mismatched samples is 3 out of 20 samples

Simulation finished at 102 ps
Mismatches: 3 in 20 samples", 
"trace_level": 2}```


[waveform_trace_tool Example 2]: Use the signal waveform to debug for functional error. You must do not change the response! 
*** Response from verilog_simulation_tool ***
[Compiled Success]
[Function Check Failed]
VCD info: dumpfile wave.vcd opened for output.
VCD warning: $dumpvars: Package ($unit) is not dumpable with VCD.
Hint: Output 'A' has 10 mismatches.
Hint: Total mismatched samples is 10 out of 2000 samples

Simulation finished at 10200 ps
Mismatches: 10 in 2000 samples
*********************************************

Action: Call waveform_trace_tool tool to debug the functional error from the simulation tool response of generated verilog code
Action Input: ```{
"function_check_output": "[Compiled Success]
[Function Check Failed]
VCD info: dumpfile wave.vcd opened for output.
VCD warning: $dumpvars: Package ($unit) is not dumpable with VCD.
Hint: Output 'A' has 10 mismatches.
Hint: Total mismatched samples is 10 out of 2000 samples

Simulation finished at 10200 ps
Mismatches: 10 in 2000 samples", 
"trace_level": 3}```

"""

RecallSpecToolExample="""
[Recall spec tool Example]: Recall and check the consistency of the spec and generated verilog code
Action: Call recall_spec_and_generated_verilog_code_tool tool to check the consistency of the spec and generated verilog code
Action Input: ```{}```

"""

SequentialFlipflopLatchToolExample="""
[Tool Example]: Identify the given waveform is a flip-flop or a latch
Action: Call sequential_flipflop_latch_identify_tool tool to identify the given waveform us a flip-flop or a latch
Action Input: ```{"sequential_signal_name": "Q",
               "time_sequence": "5ns 10ns 15ns ...",
               "clock_waveform": "0 1 0 1 ...",
               "sequential_signal_waveform": "1 0 0 1 ..."}```
               
"""
