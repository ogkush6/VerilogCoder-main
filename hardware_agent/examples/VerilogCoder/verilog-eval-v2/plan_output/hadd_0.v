module TopModule
(
  input  logic a,
  input  logic b,
  output logic sum,
  output logic cout
);

  // Combinational logic for sum
  assign sum = a ^ b;

  // Combinational logic for cout
  assign cout = a & b;

endmodule