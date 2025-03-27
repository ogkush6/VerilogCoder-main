module TopModule
(
  input  logic clk,
  input  logic w,
  input  logic R,
  input  logic E,
  input  logic L,
  output logic Q
);

  // Register to hold the current state of the output Q
  logic Q_reg;

  always @(posedge clk) begin
    if (L)
      Q_reg <= R;
    else if (E)
      Q_reg <= w;
  end

  assign Q = Q_reg;
endmodule