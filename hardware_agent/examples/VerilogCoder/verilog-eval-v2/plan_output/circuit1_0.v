module TopModule
(
  input  logic a,
  input  logic b,
  output logic q
);

  // Combinational logic for q
  assign q = a & b;

endmodule