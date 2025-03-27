module TopModule
(
  input  logic clk,
  input  logic reset,
  output logic [3:0] q
);

  // 4-bit register to hold the current state of the counter
  logic [3:0] reg_q;

  always @(posedge clk) begin
    if (reset)
      reg_q <= 4'b0000;  // Reset the counter to 0 when reset signal is high
    else if (reg_q == 4'b1001)
      reg_q <= 4'b0000;  // Reset the counter to 0 when it reaches 9
    else
      reg_q <= reg_q + 1;  // Increment the counter on the positive edge of the clock
  end

  assign q = reg_q;

endmodule