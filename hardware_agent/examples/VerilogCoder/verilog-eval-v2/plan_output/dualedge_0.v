module TopModule
(
  input  logic clk,
  input  logic d,
  output logic q
);

  // Register to store the current state of the flip-flop
  logic q_reg;

  // Sequential logic to update the flip-flop's state on both edges of the clock
  always @(posedge clk or negedge clk) begin
    q_reg <= d;
  end

  // Output assignment
  assign q = q_reg;

endmodule