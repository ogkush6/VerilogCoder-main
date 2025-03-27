module TopModule
(
  input  logic clk,
  input  logic L,
  input  logic q_in,
  input  logic r_in,
  output logic Q
);

  // Flipflop
  logic q_reg;

  // Initialize q_reg
  initial begin
    q_reg = 0;
  end

  always @(posedge clk) begin
    if (L)
      q_reg <= r_in;
    else
      q_reg <= q_in;
  end

  assign Q = q_reg;

endmodule