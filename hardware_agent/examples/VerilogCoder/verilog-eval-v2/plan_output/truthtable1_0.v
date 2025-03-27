module TopModule
(
  input  logic x3,
  input  logic x2,
  input  logic x1,
  output logic f
);

  // Combinational logic for output f
  always @(*) begin
    if (!x3 && x2)
      f = 1'b1;
    else if (x3 && !x2 && x1)
      f = 1'b1;
    else if (x3 && !x2 && !x1)
      f = 1'b0;
    else if (x3 && x2 && !x1)
      f = 1'b0;
    else if (x3 && x2 && x1)
      f = 1'b1;
    else if (!x3 && !x2) // default case for x3=0, x2=0
      f = 1'b0;
    else
      f = 1'b0; // default case
  end
endmodule