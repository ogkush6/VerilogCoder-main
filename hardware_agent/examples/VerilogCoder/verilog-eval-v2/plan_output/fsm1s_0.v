module TopModule
(
  input  logic clk,
  input  logic reset,
  input  logic in,
  output logic out
);

  // State encoding
  localparam STATE_B = 1'b0;
  localparam STATE_A = 1'b1;

  // State register
  logic state;
  always @(posedge clk) begin
    if (reset)
      state <= STATE_B;
    else
      state <= state_next;
  end

  // Next state logic
  logic state_next;
  always @(*) begin
    case(state)
      STATE_B: state_next = (in == 1'b0) ? STATE_A : STATE_B;
      STATE_A: state_next = (in == 1'b0) ? STATE_B : STATE_A;
    endcase
  end

  // Output logic
  always @(*) begin
    case(state)
      STATE_B: out = 1'b1;
      STATE_A: out = 1'b0;
    endcase
  end

endmodule