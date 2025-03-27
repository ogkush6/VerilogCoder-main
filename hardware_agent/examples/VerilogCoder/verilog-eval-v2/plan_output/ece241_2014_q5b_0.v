module TopModule
(
  input  logic clk,
  input  logic areset,
  input  logic x,
  output logic z
);

  // State encoding
  localparam STATE_A = 2'b01; // One-hot encoding for state A
  localparam STATE_B = 2'b10; // One-hot encoding for state B

  // State register
  logic [1:0] state;
  logic [1:0] state_next;

  // Asynchronous active-high reset logic
  always @(posedge clk or posedge areset) begin
    if (areset)
      state <= STATE_A;
    else
      state <= state_next;
  end

  // Next state combinational logic
  always @(*) begin
    state_next = state;
    case ( state )
      STATE_A: state_next = ( x ) ? STATE_B : STATE_A;
      STATE_B: state_next = STATE_B; // Stay in state B for both x=0 and x=1
      default: state_next = state;
    endcase
  end

  // Output combinational logic
  always @(*) begin
    z = 1'b0; // Default output
    case ( state )
      STATE_A: z = x; // Output z should be 0 when x=0 and 1 when x=1 in state A
      STATE_B: z = ~x; // Output z should be 1 when x=0 and 0 when x=1 in state B
    endcase
  end

endmodule