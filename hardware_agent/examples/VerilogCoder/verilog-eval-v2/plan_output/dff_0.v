module TopModule
(
  input  logic clk,
  input  logic d,
  output logic q
);

  // Register to hold the state of the D flip-flop
  logic q_reg;

  always @(posedge clk) begin
    q_reg <= d;
  end

  assign q = q_reg;

endmodule