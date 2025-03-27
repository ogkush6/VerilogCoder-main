module TopModule
(
  input  logic clk,
  input  logic resetn,
  input  logic in,
  output logic out
);

  // 4-bit shift register
  logic [3:0] shift_reg;

  always @(posedge clk) begin
    if (!resetn)
      shift_reg <= 4'b0000;
    else
      shift_reg <= {shift_reg[2:0], in};
  end

  // Connect the output of the last D flip-flop to the output port 'out'
  assign out = shift_reg[3];
endmodule