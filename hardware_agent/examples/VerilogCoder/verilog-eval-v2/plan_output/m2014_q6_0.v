module TopModule
(
  input  logic clk,
  input  logic reset,
  input  logic w,
  output logic z
);

  // State encoding
  localparam STATE_A = 3'b000;
  localparam STATE_B = 3'b001;
  localparam STATE_C = 3'b010;
  localparam STATE_D = 3'b011;
  localparam STATE_E = 3'b100;
  localparam STATE_F = 3'b101;

  // State register
  logic [2:0] state;
  logic [2:0] next_state;

  // Next state logic
  always @(*) begin
    next_state = state; // Default case, state remains the same
    case (state)
      STATE_A: next_state = w ? STATE_A : STATE_B;
      STATE_B: next_state = w ? STATE_D : STATE_C;
      STATE_C: next_state = w ? STATE_D : STATE_E;
      STATE_D: next_state = w ? STATE_A : STATE_F;
      STATE_E: next_state = w ? STATE_D : STATE_E;
      STATE_F: next_state = w ? STATE_D : STATE_C;
    endcase
  end

  // State transition
  always @(posedge clk) begin
    if (reset)
      state <= STATE_A;
    else
      state <= next_state;
  end

  // Output logic
  always @(*) begin
    case (state)
      STATE_E, STATE_F: z = 1'b1;
      default: z = 1'b0;
    endcase
  end

endmodule