module TopModule
(
  input  logic a,
  input  logic b,
  input  logic sel,
  output logic out
);

  // Implement the logic for the output 'out' based on the selection signal 'sel'
  assign out = sel ? b : a;

endmodule