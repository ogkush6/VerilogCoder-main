module TopModule
(
  input  logic a,
  input  logic b,
  output logic out
);

  // NOR gate logic
  assign out = ~(a | b);

endmodule