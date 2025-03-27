module TopModule
(
  input  logic [5:0] y,
  input  logic       w,
  output logic       Y1,
  output logic       Y3
);

  // Logic for next-state signal Y1
  assign Y1 = y[0] & ~w;

  // Logic for next-state signal Y3
  assign Y3 = (y[1] & w) | (y[2] & w) | (y[4] & w) | (y[5] & w);

endmodule