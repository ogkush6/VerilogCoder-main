module TopModule
(
  input  logic a,
  input  logic b,
  input  logic c,
  input  logic d,
  output logic q
);

  // Updated combinational logic for output 'q'
  assign q = (b & d) | (a & (c | d)) | (b & c);

endmodule