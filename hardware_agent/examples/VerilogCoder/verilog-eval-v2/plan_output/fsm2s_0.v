module TopModule
(
  input  logic clk,
  input  logic reset,
  input  logic j,
  input  logic k,
  output logic out
);

  // State encoding
  localparam [1:0] OFF = 2'b00;
  localparam [1:0] ON  = 2'b01;

  // State register
  logic [1:0] state;
  logic [1:0] next_state;

  always @(posedge clk) begin
    if (reset)
      state <= OFF;
    else
      state <= next_state;
  end

  // Next state logic
  always @(*) begin
    case(state)
      OFF: next_state = j ? ON : OFF;
      ON:  next_state = k ? OFF : ON;
      default: next_state = OFF;
    endcase
  end

  // Output logic
  always @(*) begin
    case(state)
      OFF: out = 0;
      ON:  out = 1;
      default: out = 0;
    endcase
  end

endmodule