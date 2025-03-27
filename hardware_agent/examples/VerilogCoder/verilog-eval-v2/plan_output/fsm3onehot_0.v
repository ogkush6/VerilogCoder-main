module TopModule
(
  input  logic       in,
  input  logic [3:0] state,
  output logic [3:0] next_state,
  output logic       out
);

  // State encoding
  localparam A = 4'b0001;
  localparam B = 4'b0010;
  localparam C = 4'b0100;
  localparam D = 4'b1000;

  // Combinational logic for next state when 'in' is 0
  always @(*) begin
    if (in == 1'b0) begin
      next_state = 4'b0000;
      if (state[0] == 1'b1) // State A
        next_state[0] = 1'b1; // Next state is A
      if (state[1] == 1'b1) // State B
        next_state[2] = 1'b1; // Next state is C
      if (state[2] == 1'b1) // State C
        next_state[0] = 1'b1; // Next state is A
      if (state[3] == 1'b1) // State D
        next_state[2] = 1'b1; // Next state is C
    end
    else if (in == 1'b1) begin
      next_state = 4'b0000;
      if (state[0] == 1'b1) // State A
        next_state[1] = 1'b1; // Next state is B
      if (state[1] == 1'b1) // State B
        next_state[1] = 1'b1; // Next state is B
      if (state[2] == 1'b1) // State C
        next_state[3] = 1'b1; // Next state is D
      if (state[3] == 1'b1) // State D
        next_state[1] = 1'b1; // Next state is B
    end
  end

  // Combinational logic for output
  always @(*) begin
    out = 1'b0;
    if (state[3] == 1'b1) // State D
      out = 1'b1; // Output is 1
  end

endmodule