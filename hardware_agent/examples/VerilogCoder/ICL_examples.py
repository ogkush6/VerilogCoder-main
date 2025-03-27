#
# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# Author : Chia-Tung (Mark) Ho, NVIDIA
#

# For circuit8 ICL to identify the flip-flops and latch
SequentialCircuitExample="""
For simulation waveform, if it is a sequential circuit, be attention to the output and input signal transitions at clock edge (0 -> 1 posedge, or 1-> 0 negedge for flip-flops), or during active high period of clock for latch.
Flip-flop only change the value when clk is transition 0 to 1 or 1 to 0 edge, and the value of Flip-Flop will not changed in the waveform. 
Latch is transparent and change the value when clk is active. Below are examples.
  
  [Positive edge triggered Flip-Flops Example]
  ### Verilog:
  always@(posedge clk) begin
    q <= din;
  end
  
  ### Flip-Flop Waveform
  time  clk  din  q
  ...
  30ns  0  1  x
  35ns  0  1  x (posedge clk triggered)
  40ns  1  1  1 (posedge clk triggered storing din=1 at 35ns)
  45ns  1  0  1
  50ns  1  0  1
  55ns  0  0  1
  60ns  0  0  1 (posedge clk triggered)
  65ns  1  0  0 (posedge clk triggered storing din=0 at 60ns)
  70ns  1  1  0
  75ns  1  1  0
  ...
  [Positive edge triggered Flip-Flops Example]
  
  [Negative edge triggered Flip-Flops Example]
  ### Verilog:
  always@(negedge clk) begin
    q <= din;
  end
  
  ### Flip-Flop Waveform
  time  clk  din  q
  ...
  30ns  0  1  x
  35ns  0  1  x 
  40ns  1  1  x 
  45ns  1  0  x
  50ns  1  0  x (negedge clk triggered)
  55ns  0  0  0 (negedge clk triggered storing din=0 at 50ns)
  60ns  0  0  0 
  65ns  1  0  0 
  70ns  1  1  0
  75ns  1  1  0
  ...
  [Negative edge triggered Flip-Flops Example]
  
  [Latch Example]
  ### Verilog:
  always@(*) begin
    if (clk) begin
        q = din;
    end
  end
  
  ### Latch Waveform
  time  clk  din  q
  ...
  30ns  0  1  0
  35ns  0  1  0
  40ns  1  1  1 (active clk period store din)
  45ns  1  0  0 (active clk period store din)
  50ns  1  1  1 (active clk period store din)
  55ns  0  0  1
  ...
  [Latch Example]
"""

InitializeExample="""
### Problem

I would like you to implement a module named TopModule with the following
interface. All input and output ports are one bit unless otherwise
specified.
 
 - input  clk
 - input  in (4 bits)
 - output out (4 bits)

The module should implement an 4-bit registered. The 4-bit
input is first registered and then output to the out. The initial value 
of the register is 4'b0000.

Assume all sequential logic is triggered on the positive edge of the
clock. 

### Solution

module TopModule
(
  input  logic       clk,
  input  logic [3:0] in,
  output logic [3:0] out
);
  logic [3:0] q;
  initial
    q = 4'b0000;
  
  always @ (posedge clk) begin
    q <= in;
  end

endmodule

"""

GeneralExample="""
### Problem

I would like you to implement a module named TopModule with the following
interface. All input and output ports are one bit unless otherwise
specified.

 - input  clk
 - input  reset
 - input  in (8 bits)
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
  input  logic [7:0] in,
  output logic [7:0] out
);

  // Sequential logic

  logic [7:0] reg_out;

  always @( posedge clk ) begin
    if ( reset )
      reg_out <= 0;
    else
      reg_out <= in;
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
 - input  in
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
  input  logic in,
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
    if ( reset ) begin
      state <= STATE_A;
    end else begin
      state <= state_next;
    end
  end

  // Next state combinational logic

  always @(*) begin
    state_next = state;
    case ( state )
      STATE_A: state_next = ( in ) ? STATE_B : STATE_A;
      STATE_B: state_next = ( in ) ? STATE_C : STATE_A;
      STATE_C: state_next = ( in ) ? STATE_C : STATE_A;
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
"""

# BCD counter
BCDCounterExample="""
3-digit BCD Example: 
The following TopModule implement a 3-digit BCD (binary-coded decimal) counter. 
Each decimal digit is encoded using 4 bits: q[3:0] is the ones digit,
q[7:4] is the tens digit, and so on. Also output an enable (ena [1:0]) signal indicating 
when each of the upper two digits should be incremented. Include a synchronous 
active-high reset. Assume all sequential logic is triggered on 
the positive edge of the clock.

module top_module (
    input clk,
    input reset,   // Synchronous active-high reset
    output [1:0] ena,
    output [11:0] q);

    // Internal signal for the ones, tens, hundreds, and thousands digits
    logic [3:0] ones_digit;
    logic [3:0] tens_digit;
    logic [3:0] hundreds_digit;
    assign ena[0] = ones_digit == 4'b1001; // enable for the ten-digits
    assign ena[1] = {tens_digit, ones_digit} == 8'b10011001; // enable for the hundreds-digits; 99
    assign overflow = {hundreds-digits, tens_digit, ones_digit} == 12'b100110011001; // overflow 999
    // Sequential logic for the ones digit counter
    always @(posedge clk) begin
        if (reset) begin
            ones_digit <= 4'b0000; // Reset the ones digit to 0
        end else begin
            if (ones_digit == 4'b1001) begin // If ones digit is 9
                ones_digit <= 4'b0000;       // Reset to 0
            end else begin
                ones_digit <= ones_digit + 1'b1; // Increment ones digit
            end
        end
    end

    // Sequential logic for the tens digit counter
    always @(posedge clk) begin
        if (reset) begin
            tens_digit <= 4'b0000; // Reset the tens digit to 0
        end else if (ena[0]) begin
            if (ena[1]) begin
                tens_digit <= 4'b0000;
            end else begin
                tens_digit <= tens_digit + 1'b1; // Increment ones digit
            end
        end
    end
    
    // Sequential logic for the hundreds_digit digit counter
    always @(posedge clk) begin
        if (reset) begin
            hundreds_digit <= 4'b0000; // Reset the tens digit to 0
        end else if (ena[2]) begin
            if overflow begin
                hundreds_digit <= 4'b0000; // Reset to zero
            end else begin
            	hundreds_digit <= hundreds_digit + 1'b1; // Increment ones digit
            end
        end
    end

    assign q[3:0] = ones_digit;
    assign q[7:4] = tens_digit;
    assign q[11:8] = hundreds_digit;

endmodule
"""

#lemmings examples
LemmingsExample="""
[lemmings3 Example]:
The following TopModule implement the game Lemmings involves critters 
with fairly simple brains. So simple that we are going to model it using 
a finite state machine. 

- In the Lemmings' 2D world, Lemmings can be in the states: walking left 
(walk_left is 1) or walking right (walk_right is 1). It will switch directions 
if it hits an obstacle. In particular, if a Lemming is bumped on the left 
(by receiving a 1 on bump_left), it will walk right. If it's bumped on the right 
(by receiving a 1 on bump_right), it will walk left.

- When ground=0, the Lemming will fall and say "aaah!". When the ground
reappears (ground=1), the Lemming will resume walking in the same
direction as before the fall. The fall (ground=0) status can be consecutively 
more than once, Lemming need to remain the walking left or walking right 
status when fall. Being bumped while falling does not affect
the walking direction, and being bumped in the same cycle as ground
disappears (but not yet falling), or when the ground reappears while
still falling, also does not affect the walking direction.

- Lemmings can also be told to do useful things, like dig (it starts digging 
when dig=1). A Lemming can dig if it is currently walking on ground (ground=1 
and not falling), and will continue digging until it reaches the other 
side (ground=0). At that point, since there is no ground, it will fall (aaah!), 
then continue walking in its original direction once it hits ground again. 
Lemming need to remain the walking left or walking right status before fall. 

In summary, a walking Lemming can fall, dig, or switch directions. If more than 
one of these conditions are satisfied, fall has higher precedence than dig,
which has higher precedence than switching directions.)

[lemmings3 Implementation Example]:
module TopModule
(
  input  logic clk,
  input  logic areset,
  input  logic bump_left,
  input  logic bump_right,
  input  logic ground,
  input  logic dig,
  output logic walk_left,
  output logic walk_right,
  output logic aaah,
  output logic digging
);

  // State enum
  localparam WALKING_LEFT  = 2'b00;
  localparam WALKING_RIGHT = 2'b01;
  localparam FALLING       = 2'b10;
  localparam DIGGING       = 2'b11;

  // State register
  logic [1:0] state;
  logic [1:0] state_next;
  logic [1:0] state_before_fall; // to remember the state before falling

  // Asynchronous reset logic
  always @(posedge clk or posedge areset) begin
    if (areset) begin
      state <= WALKING_LEFT;
      state_before_fall <= WALKING_LEFT;
    end
    else
      state <= state_next;
  end

  // Next state combinational logic
  always @(*) begin
    state_next = state;
    case (state)
      WALKING_LEFT: begin
        if (!ground)
          state_next = FALLING;
        else if (dig)
          state_next = DIGGING;
        else if (bump_left || (bump_left && bump_right))
          state_next = WALKING_RIGHT;
        else
          state_next = WALKING_LEFT;
      end
      WALKING_RIGHT: begin
        if (!ground)
          state_next = FALLING;
        else if (dig)
          state_next = DIGGING;
        else if (bump_right || (bump_left && bump_right))
          state_next = WALKING_LEFT;
        else
          state_next = WALKING_RIGHT;
      end
      FALLING: begin
        if (ground)
          state_next = state_before_fall; // Correctly resume previous walking state
        else
          state_next = FALLING;
      end
      DIGGING: begin
        if (!ground)
          state_next = FALLING;
        else
          state_next = DIGGING;
      end
      default: state_next = state;
    endcase
  end

  // Save the state before falling
  always @(posedge clk) begin
    if (state_next == FALLING)
      state_before_fall <= state;
  end

  // Output logic for walk_left and walk_right
  always @(*) begin
    walk_left = (state == WALKING_LEFT) ? 1'b1 : 1'b0;
    walk_right = (state == WALKING_RIGHT) ? 1'b1 : 1'b0;
  end

  // Output logic for aaah
  always @(*) begin
    aaah = (state == FALLING) ? 1'b1 : 1'b0;
  end

  // Output logic for digging
  always @(*) begin
    digging = (state == DIGGING) ? 1'b1 : 1'b0;
  end

endmodule
"""

SumOfProductToProductOfSumExample="""
The product-of-sum (pos) is the logical inverse of `the sum-of-product (sop_logic0) when output is logic-0`, and then apply Demorgan's Theorem.

### Steps Example of pos derive from logic 0 ###
For example, given input (ab), output logic is 1 when input equals to 0 (ab=2'b00) and 3 (ab=2'b11). 
When input equals to 1 (ab=2'b01) and 2 (ab=2'b10), the output logic is 0.

To derive product-of-sum (pos) of above example steps by steps.
Step 1. Derive the sop for output logic is 0. Create the sop_logic0. 
        sop_logic0 = (~a & b) |   // 1 (2'b01) 
                     (a & ~b)     // 2 (2'b10)
Step 2. pos = ~(sop_logic0) = ~((~a & b) | (a & ~b))
                            = ~(~a & b) & ~(a & ~b) // applying Demorgan's Theorem. 
Step 3. pos = (a | ~b) &  // Demorgan's Theorem for ~(~a & b) 
              (~a | b)    // Demorgan's Theorem for ~(a & ~b) 
### Steps Example of pos derive from logic 0 End ###

"""

Q3FSM2014="""

[Implementation Example]:
```verilog
module TopModule (
    input  logic clk,
    input  logic reset,
    input  logic s,
    input  logic w,
    output logic z
);

    // State Definitions
    localparam STATE_A  = 3'b000;
    localparam STATE_B  = 3'b001;
    localparam STATE_B1 = 3'b010;
    localparam STATE_B2 = 3'b011;
    localparam STATE_Z  = 3'b100;

    // State Register
    logic [2:0] state;
    logic [2:0] next_state;

    // Variables to track the input 'w' across states
    logic pre_w;      // Previous 'w' value
    logic pre_pre_w;  // 'w' value before previous

    // Sequential logic for state transitions
    always @(posedge clk) begin
        if (reset) begin
            state <= STATE_A;
            pre_w <= 0;
            pre_pre_w <= 0;
         end else begin
            state <= next_state;
            pre_pre_w <= pre_w;
            pre_w <= w;
        end
    end

    // Combinational logic for next state logic
    always @(*) begin
        case (state)
            STATE_A: next_state = s ? STATE_B : STATE_A;
            STATE_B: next_state = STATE_B1;
            STATE_B1: next_state = (pre_w == 0 && w == 0) ? STATE_B : STATE_B2;
            STATE_B2: next_state = ((pre_pre_w && pre_w && !w) || (!pre_pre_w && pre_w && w) || (pre_pre_w && !pre_w && w)) ? STATE_Z : STATE_B;
            STATE_Z: next_state = STATE_B1;
            default: next_state = STATE_A;
        endcase
    end

    // Output logic
    always @(*) begin
        z = (state == STATE_Z);
    end

endmodule
```
"""
