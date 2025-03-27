module TopModule
(
  input  logic in1,
  input  logic in2,
  input  logic in3,
  output logic out
);

  // Combinational logic

  logic xnor_result;

  assign xnor_result = ~(in1 ^ in2);
  assign out = xnor_result ^ in3;

endmodule