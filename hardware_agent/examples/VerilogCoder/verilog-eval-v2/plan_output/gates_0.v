module TopModule
(
  input  logic a,
  input  logic b,
  output logic out_and,
  output logic out_or,
  output logic out_xor,
  output logic out_nand,
  output logic out_nor,
  output logic out_xnor,
  output logic out_anotb
);

  // Combinational logic for out_and
  assign out_and = a & b;

  // Combinational logic for out_or
  assign out_or = a | b;

  // Combinational logic for out_xor
  assign out_xor = a ^ b;

  // Combinational logic for out_nand
  assign out_nand = ~(a & b);

  // Combinational logic for out_nor
  assign out_nor = ~(a | b);

  // Combinational logic for out_xnor
  assign out_xnor = ~(a ^ b);

  // Combinational logic for out_anotb
  assign out_anotb = a & ~b;

endmodule