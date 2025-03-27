module TopModule
(
  input  logic clk,
  input  logic reset,
  output logic [9:0] q
);

  // 10-bit register to hold the current count value
  logic [9:0] count_reg;

  always @(posedge clk) begin
    if (reset)
      count_reg <= 10'b0; // reset the counter to 0
    else if (count_reg == 999)
      count_reg <= 10'b0; // wrap around to 0 if counter reaches 999
    else
      count_reg <= count_reg + 1; // increment the counter
  end

  assign q = count_reg;

endmodule