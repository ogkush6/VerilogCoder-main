module TopModule
(
  input  logic clk,
  input  logic reset,
  input  logic w,
  output logic z
);

  // State encoding
  localparam [2:0] STATE_A = 3'b000;
  localparam [2:0] STATE_B = 3'b001;
  localparam [2:0] STATE_C = 3'b010;
  localparam [2:0] STATE_D = 3'b011;
  localparam [2:0] STATE_E = 3'b100;
  localparam [2:0] STATE_F = 3'b101;

  // State register
  logic [2:0] state;
  logic [2:0] state_next;

  // State flip-flop logic block
  always @(posedge clk) begin
    if (reset)
      state <= STATE_A;
    else
      state <= state_next;
  end

  // Next state logic block
  always @(*) begin
    state_next = state;
    case (state)
      STATE_A: state_next = w ? STATE_B : STATE_A;
      STATE_B: state_next = w ? STATE_C : STATE_D;
      STATE_C: state_next = w ? STATE_E : STATE_D;
      STATE_D: state_next = w ? STATE_F : STATE_A;
      STATE_E: state_next = w ? STATE_E : STATE_D;
      STATE_F: state_next = w ? STATE_C : STATE_D;
    endcase
  end

  // Output logic block
  always @(*) begin
    z = 1'b0;
    case (state)
      STATE_E: z = 1'b1;
      STATE_F: z = 1'b1;
      default: z = 1'b0;
    endcase
  end

endmodule