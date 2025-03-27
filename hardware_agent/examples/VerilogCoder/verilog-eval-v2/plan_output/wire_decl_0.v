module TopModule
(
  input  logic a,
  input  logic b,
  input  logic c,
  input  logic d,
  output logic out,
  output logic out_n
);

  // Intermediate wires
  logic wire1;
  logic wire2;

  // AND gates
  assign wire1 = a & b; // Implement the first AND gate with inputs a and b, and connect the output to wire1.
  assign wire2 = c & d; // Implement the second AND gate with inputs c and d, and connect the output to wire2.

  // OR gate
  assign out = wire1 | wire2;

  // NOT gate
  assign out_n = ~out;

endmodule