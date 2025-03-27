module TopModule
(
  input  logic clk,
  input  logic reset,
  input  logic in,
  output logic out
);

  // State encoding
  localparam STATE_A = 2'b00;
  localparam STATE_B = 2'b01;
  localparam STATE_C = 2'b10;
  localparam STATE_D = 2'b11;

  // State register
  logic [1:0] state;
  logic [1:0] state_next;

  always @(posedge clk) begin
    if (reset) begin
      state <= STATE_A;
    end else begin
      state <= state_next;
    end
  end

  // Next state combinational logic
  always @(*) begin
    case (state)
      STATE_A: state_next = in ? STATE_B : STATE_A;
      STATE_B: state_next = in ? STATE_B : STATE_C;
      STATE_C: state_next = in ? STATE_D : STATE_A;
      STATE_D: state_next = in ? STATE_B : STATE_C;
      default: state_next = STATE_A;
    endcase
  end

  // Output combinational logic
  always @(*) begin
    case (state)
      STATE_A: out = 1'b0;
      STATE_B: out = 1'b0;
      STATE_C: out = 1'b0;
      STATE_D: out = 1'b1;
      default: out = 1'b0;
    endcase
  end

endmodule