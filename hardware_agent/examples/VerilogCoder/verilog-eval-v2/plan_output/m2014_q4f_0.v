module TopModule
(
  input  logic in1,
  input  logic in2,
  output logic out
);

  // Invert the input in2 to create a new signal
  logic in2_bubble;
  assign in2_bubble = ~in2;

  // Implement AND gate logic using in1 and in2_bubble
  assign out = in1 & in2_bubble;

endmodule