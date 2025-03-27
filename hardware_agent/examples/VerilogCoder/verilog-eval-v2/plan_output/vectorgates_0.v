module TopModule
(
  input  logic [2:0] a,
  input  logic [2:0] b,
  output logic [2:0] out_or_bitwise,
  output logic       out_or_logical,
  output logic [5:0] out_not
);

  // Bitwise OR operation
  assign out_or_bitwise = a | b;

  // Logical OR operation
  assign out_or_logical = |a | |b;

  // NOT operation on 'a' and assign to lower half of 'out_not'
  assign out_not[2:0] = ~a;

  // NOT operation on 'b' and assign to upper half of 'out_not'
  assign out_not[5:3] = ~b;

endmodule