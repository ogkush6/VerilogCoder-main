module TopModule
(
  input  logic a,
  input  logic b,
  input  logic c,
  input  logic d,
  output logic q
);

  // Combinational logic
  always @(*) begin
    if (!a && !b && !c && !d)
      q = 1'b1;
    else if (!a && !b && !c && d)
      q = 1'b0;
    else if (!a && !b && c && !d)
      q = 1'b0;
    else if (!a && !b && c && d)
      q = 1'b1;
    else if (!a && b && !c && !d)
      q = 1'b0;
    else if (!a && b && !c && d)
      q = 1'b1;
    else if (!a && b && c && !d)
      q = 1'b1;
    else if (!a && b && c && d)
      q = 1'b0;
    else if (a && !b && !c && !d)
      q = 1'b0;
    else if (a && !b && !c && d)
      q = 1'b1;
    else if (a && !b && c && !d)
      q = 1'b1;
    else if (a && !b && c && d)
      q = 1'b0;
    else if (a && b && !c && !d)
      q = 1'b1;
    else if (a && b && !c && d)
      q = 1'b0;
    else if (a && b && c && !d)
      q = 1'b0;
    else if (a && b && c && d)
      q = 1'b1;
  end
endmodule