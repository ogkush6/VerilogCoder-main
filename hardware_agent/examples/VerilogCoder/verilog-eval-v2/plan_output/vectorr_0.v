module TopModule
(
  input  logic [7:0] in,
  output logic [7:0] out
);

  // Output register
  logic [7:0] out_reg;

  always @(*) begin
    out_reg[7] = in[0];
    out_reg[6] = in[1];
    out_reg[5] = in[2];
    out_reg[4] = in[3];
    out_reg[3] = in[4];
    out_reg[2] = in[5];
    out_reg[1] = in[6];
    out_reg[0] = in[7];
  end

  // Structural connections
  assign out = out_reg;

endmodule