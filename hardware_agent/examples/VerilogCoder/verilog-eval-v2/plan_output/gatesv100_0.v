module TopModule
(
  input  logic [99:0] in,
  output logic [99:0] out_both,
  output logic [99:0] out_any,
  output logic [99:0] out_different
);

  // Combinational logic for out_both
  assign out_both[99] = 1'b0; // No left neighbour for in[99]
  genvar i;
  generate
    for (i = 0; i < 99; i = i + 1) begin
      assign out_both[i] = in[i] & in[i+1];
    end
  endgenerate

  // Combinational logic for out_any
  assign out_any[0] = 1'b0; // No right neighbour for in[0]
  generate
    for (i = 1; i < 100; i = i + 1) begin
      assign out_any[i] = in[i] | in[i-1];
    end
  endgenerate

  // Combinational logic for out_different
  assign out_different[99] = in[99] ^ in[0]; // For in[99], left neighbour is in[0]
  generate
    for (i = 0; i < 99; i = i + 1) begin
      assign out_different[i] = in[i] ^ in[i+1];
    end
  endgenerate

endmodule