module TopModule
(
  input  logic clk,
  input  logic reset,
  input  logic slowena,
  output logic [3:0] q
);

  // 4-bit register for the decade counter
  logic [3:0] counter;

  always @(posedge clk) begin
    if (reset)
      counter <= 4'b0000;  // Reset counter to 0
    else if (slowena) begin
      if (counter == 4'b1001)  // If counter is 9
        counter <= 4'b0000;  // Wrap around to 0
      else
        counter <= counter + 1'b1;  // Increment counter
    end
  end

  assign q = counter;

endmodule