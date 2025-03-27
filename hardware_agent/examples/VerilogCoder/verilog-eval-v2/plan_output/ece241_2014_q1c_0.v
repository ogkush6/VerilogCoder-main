module TopModule
(
  input  logic [7:0] a,
  input  logic [7:0] b,
  output logic [7:0] s,
  output logic overflow
);

  // Combinational logic for sum
  assign s = a + b;

  // Combinational logic for overflow
  assign overflow = ((a[7] == b[7]) && (s[7] != a[7]));

endmodule