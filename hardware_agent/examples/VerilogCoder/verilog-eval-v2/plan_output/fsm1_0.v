module TopModule
(
  input  logic clk,
  input  logic areset,
  input  logic in,
  output logic out
);

  // State enum
  localparam STATE_A = 1'b0;
  localparam STATE_B = 1'b1;

  // State register
  logic state;
  logic state_next;

  // Asynchronous reset
  always @(posedge clk or posedge areset) begin
    if (areset)
      state <= STATE_B;
    else
      state <= state_next;
  end

  // Next state logic
  always @(*) begin
    case (state)
      STATE_A: state_next = (in == 1'b0) ? STATE_B : STATE_A;
      STATE_B: state_next = (in == 1'b0) ? STATE_A : STATE_B;
      default: state_next = STATE_B;
    endcase
  end

  // Output logic
  always @(*) begin
    case (state)
      STATE_A: out = 1'b0;
      STATE_B: out = 1'b1;
      default: out = 1'b0;
    endcase
  end

endmodule