module TopModule
(
  input  logic [2:0] vec,
  output logic [2:0] outv,
  output logic o2,
  output logic o1,
  output logic o0
);

  // Assign the first bit of the input vector 'vec' to the output 'o0'.
  assign o0 = vec[0];

  // Assign the second bit of the input vector 'vec' to the output 'o1'.
  assign o1 = vec[1];

  // Assign the third bit of the input vector 'vec' to the output 'o2'.
  assign o2 = vec[2];

  // Assign the entire 3-bit input vector 'vec' directly to the 3-bit output 'outv'.
  assign outv = vec;

endmodule