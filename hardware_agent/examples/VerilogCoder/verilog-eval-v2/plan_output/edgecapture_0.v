module TopModule (
  input  logic clk,
  input  logic reset,
  input  logic [31:0] in,
  output logic [31:0] out
);

  // Define a 32-bit register to store the previous state of the input vector 'in'
  logic [31:0] prev_in;

  // Sequential logic to update the previous state register and the output register
  always @(posedge clk) begin
    if (reset) begin
      // When reset is active, clear the 'out' register and store the current 'in' for the next capture
      out <= 32'b0;
      prev_in <= in;
    end else begin
      // Update the previous state register with the current 'in' vector
      prev_in <= in;
      // Capture the changes from 1 to 0 by comparing 'in' with 'prev_in'
      out <= out | (prev_in & ~in);
    end
  end

endmodule