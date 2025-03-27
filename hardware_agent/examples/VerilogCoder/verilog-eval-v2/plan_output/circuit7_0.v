module TopModule
(
  input  logic clk,
  input  logic a,
  output logic q
);

  // State register
  logic q_reg;
  logic a_prev;

  always @(posedge clk) begin
    a_prev <= a;
    if (a && !a_prev)
      q_reg <= 0;
    else if (!a)
      q_reg <= 1'b1;
    else
      q_reg <= q_reg;
  end

  assign q = q_reg;

endmodule