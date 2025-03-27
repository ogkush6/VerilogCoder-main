# VerilogCoder: Autonomous Verilog Coding Agents with Graph-based Planning and Abstract Syntax Tree (AST)-based Waveform Tracing Tool

## Description
VerilogCoder is an autonomous verilog coding agent that using graph-based planning and AST-based waveform tracing tool. The paper is in [https://arxiv.org/abs/2408.08927v1]. We use Verilog Eval Human v2 benchmarks on (https://github.com/NVlabs/verilog-eval/tree/main/dataset_spec-to-rtl) for experiments.

## LLM Models
The prompts are finetuned for GPT-4 and Llama3. User can switch to other LLM models with their own prompts.

## Benchmark and Generated .sv from VerilogCoder in the paper
- **Case Dir**: ```<project_home_dir>/hardware_agent/examples/VerilogCoder/verilog-eval-v2/```
- **Benchmark Dir**: ```<case_dir>/dataset_dumpall```
- **VerilogCoder Generated Plan Reference Dir**: ```<case_dir>/plans```
- **VerilogCoder Generated Verilog File Reference Dir**: ```<case_dir>/plan_output```

## Inputs and Outputs for VerilogCoder
- **Input**: Target RTL specification, and testbench. 
- **Output**: Completed functional correct Verilog module.

## Prerequisite Tool Installation
In order to run the waveform tracing tool, user need to install iverilog.

```
git clone https://github.com/steveicarus/iverilog.git && cd iverilog \ 
        && git checkout 01441687235135d1c12eeef920f75d97995da333 \ 
        && sh ./autoconf.sh  
./configure --prefix=<local dir> 
make –j4 
Make install 
export PATH=<local dir>:$PATH 
```

## Installation

1. Create conda environment
```
#Create conda env with python >= 3.10
conda create -n hardware_agent python=3.10.13
conda activate hardware_agent
```

2. Install the packages
```
#setup environment in conda env
pip install -e . or python setup.py install (non-editable mode)
pip install pypdf
pip install PILLOW
pip install network
pip install matplotlib
pip install pydantic==2.10.1
pip install langchain==0.3.14
pip install llangchain_openai==0.2.14
pip install langchain_community==0.3.14
pip install chromadb==0.4.24
pip install IPython 
pip install markdownify 
pip install pypdf 
pip install sentence_transformers==2.7.0
pip install -U chainlit 
export PYTHONPATH=<cur_dir_path>:$PYTHONPATH
```

## Quick Start
1. Use the OAI_CONFIG_LIST to setup the LLM models.
```
[
    {
        "model": "gpt-4-turbo",
	"api_key": ""
    }
]
```

2. make a temp working directory.
```
mkdir verilog_tool_tmp
```

3. Select the cases to run VerilogCoder in hardware_agent/examples/VerilogCoder/run_verilog_coder.py using user_task_ids.
```
# Load verilog problem sets
# Add questions
user_task_ids = {'zero'}
case_manager = VerilogCaseManager(file_path=args.verilog_example_dir, task_ids=user_task_ids)
```

4. Run the command for "python hardware_agent/examples/VerilogCoder/run_verilog_coder.py --generate_plan_dir <TCRG_plan_dir> --generate_verilog_dir <Verilog_code_dir> --verilog_example_dir <Verilog_Eval_v2_benchmark_dir>".
   
Example:
```
python hardware_agent/examples/VerilogCoder/run_verilog_coder.py --generate_plan_dir <case_dir>/plans/ --generate_verilog_dir <case_dir>/plan_output/ --verilog_example_dir <case_dir>
```

## Signing Your Work
We require that all contributors "sign-off" on their commits. This certifies that the contribution is your original work, or you have rights to submit it under the same license, or a compatible license.

Any contribution which contains commits that are not Signed-Off will not be accepted.
To sign off on a commit you simply use the --signoff (or -s) option when committing your changes:
```
$ git commit -s -m "Add cool feature."
```
This will append the following to your commit message:
```
Signed-off-by: Your Name <your@email.com>
```
Full text of the DCO:

  Developer Certificate of Origin
  Version 1.1
  
  Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
  1 Letterman Drive
  Suite D4700
  San Francisco, CA, 94129
  
  Everyone is permitted to copy and distribute verbatim copies of this license document, but changing it is not allowed.
  Developer's Certificate of Origin 1.1
  
  By making a contribution to this project, I certify that:
  
  (a) The contribution was created in whole or in part by me and I have the right to submit it under the open source license indicated in the file; or
  
  (b) The contribution is based upon previous work that, to the best of my knowledge, is covered under an appropriate open source license and I have the right under that license to submit that work with modifications, whether created in whole or in part by me, under the same open source license (unless I am permitted to submit under a different license), as indicated in the file; or
  
  (c) The contribution was provided directly to me by some other person who certified (a), (b) or (c) and I have not modified it.
  
  (d) I understand and agree that this project and the contribution are public and that a record of the contribution (including all personal information I submit with it, including my sign-off) is maintained indefinitely and may be redistributed consistent with this project or the open source license(s) involved.

