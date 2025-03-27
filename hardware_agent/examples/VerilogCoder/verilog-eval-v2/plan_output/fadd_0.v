module TopModule
(
  input  logic a,
  input  logic b,
  input  logic cin,
  output logic cout,
  output logic sum
);

  // Combinational logic for 'sum' output
  assign sum = a ^ b ^ cin;

  // Combinational logic for 'cout' output
  assign cout = (a & b) | (b & cin) | (a & cin);

endmodule