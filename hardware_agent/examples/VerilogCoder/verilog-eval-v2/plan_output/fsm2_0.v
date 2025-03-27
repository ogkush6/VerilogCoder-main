module TopModule
(
  input  logic clk,
  input  logic areset,
  input  logic j,
  input  logic k,
  output logic out
);

  // State encoding
  localparam [1:0] OFF = 2'b00;
  localparam [1:0] ON  = 2'b01;

  // State register
  logic [1:0] state;

  // Asynchronous reset logic
  always @(posedge clk or posedge areset) begin
    if (areset)
      state <= OFF;
    else
      case(state)
        OFF: state <= (j) ? ON : OFF;
        ON:  state <= (k) ? OFF : ON;
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