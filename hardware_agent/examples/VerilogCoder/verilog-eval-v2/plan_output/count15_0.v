module TopModule
(
  input  logic clk,
  input  logic reset,
  output logic [3:0] q
);

  // 4-bit register for the counter
  logic [3:0] counter;

  always @(posedge clk) begin
    if (reset)
      counter <= 4'b0000;  // Reset the counter to 0
    else
      counter <= counter + 1;  // Increment the counter
  end

  assign q = counter;  // Output the counter value

endmodule