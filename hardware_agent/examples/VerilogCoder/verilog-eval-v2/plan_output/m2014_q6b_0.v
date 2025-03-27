module TopModule
(
  input  logic [2:0] y,
  input  logic w,
  output logic Y1
);

  // State encoding
  localparam [2:0] STATE_A = 3'b000;
  localparam [2:0] STATE_B = 3'b001;
  localparam [2:0] STATE_C = 3'b010;
  localparam [2:0] STATE_D = 3'b011;
  localparam [2:0] STATE_E = 3'b100;
  localparam [2:0] STATE_F = 3'b101;

  // Next state logic for y[1]
  logic [2:0] next_state;
  always @(*) begin
    case (y)
      STATE_A: next_state = (w) ? STATE_A : STATE_B;
      STATE_B: next_state = (w) ? STATE_D : STATE_C;
      STATE_C: next_state = (w) ? STATE_D : STATE_E;
      STATE_D: next_state = (w) ? STATE_A : STATE_F;
      STATE_E: next_state = (w) ? STATE_D : STATE_E;
      STATE_F: next_state = (w) ? STATE_D : STATE_C;
      default: next_state = 3'b000;
    endcase
  end

  // Assign the output Y1 to the value of y[1] from the next state.
  assign Y1 = next_state[1];

endmodule