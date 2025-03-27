module TopModule
(
  input  logic clk,
  input  logic reset,
  output logic [3:0] q
);

  // 4-bit register to hold the current state of the counter
  logic [3:0] counter_reg;

  always @(posedge clk) begin
    if (reset)
      counter_reg <= 4'b0001; // Initialize to represent the number 1
    else if (counter_reg == 4'b1010)
      counter_reg <= 4'b0001; // Wrap around to 1 when counter reaches 10
    else
      counter_reg <= counter_reg + 1; // Increment the counter by 1
  end

  assign q = counter_reg;
endmodule