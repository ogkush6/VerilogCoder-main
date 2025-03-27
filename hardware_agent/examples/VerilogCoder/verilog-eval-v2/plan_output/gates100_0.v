module TopModule
(
  input  logic [99:0] in,
  output logic        out_and,
  output logic        out_or,
  output logic        out_xor
);

  // Combinational logic for out_and
  assign out_and = &in;

  // Combinational logic for out_or
  assign out_or = |in;

  // Combinational logic for out_xor
  assign out_xor = ^in;

endmodule