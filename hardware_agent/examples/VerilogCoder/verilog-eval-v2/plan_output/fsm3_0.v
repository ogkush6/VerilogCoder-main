module TopModule
(
  input  logic clk,
  input  logic areset,
  input  logic in,
  output logic out
);

  // State encoding
  localparam [1:0] STATE_A = 2'b00;
  localparam [1:0] STATE_B = 2'b01;
  localparam [1:0] STATE_C = 2'b10;
  localparam [1:0] STATE_D = 2'b11;

  // State register
  logic [1:0] state;
  logic [1:0] state_next;

  always @(posedge clk or posedge areset) begin
    if (areset)
      state <= STATE_A;
    else
      state <= state_next;
  end

  // Next state logic
  always @(*) begin
    state_next = state;
    case (state)
      STATE_A: state_next = in ? STATE_B : STATE_A;
      STATE_B: state_next = in ? STATE_B : STATE_C;
      STATE_C: state_next = in ? STATE_D : STATE_A;
      STATE_D: state_next = in ? STATE_B : STATE_C;
      default: state_next = state;
    endcase
  end

  // Output logic
  always @(*) begin
    case (state)
      STATE_A: out = 0;
      STATE_B: out = 0;
      STATE_C: out = 0;
      STATE_D: out = 1;
      default: out = 0;
    endcase
  end

endmodule