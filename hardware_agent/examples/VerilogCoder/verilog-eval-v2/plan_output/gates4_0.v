module TopModule
(
  input  logic [3:0] in,
  output logic out_and,
  output logic out_or,
  output logic out_xor
);

  // Combinational logic for out_and
  assign out_and = in[0] & in[1] & in[2] & in[3];

  // Combinational logic for out_or
  assign out_or = in[0] | in[1] | in[2] | in[3];

  // Combinational logic for out_xor
  assign out_xor = in[0] ^ in[1] ^ in[2] ^ in[3];

endmodule