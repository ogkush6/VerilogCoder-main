module TopModule
(
  input  logic x,
  input  logic y,
  output logic z
);

  // Combinational logic

  logic xor_result;
  logic and_result;

  assign xor_result = x ^ y;
  assign and_result = xor_result & x;

  assign z = and_result;

endmodule