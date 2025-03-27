module TopModule (
  input  logic clk,
  input  logic reset,
  output logic [4:0] q
);

  always @(posedge clk) begin
    if (reset) begin
      q <= 5'b00001; // Set LFSR output to 1 when reset is active-high
    end else begin
      q[4] <= q[0] ^ 1'b0; // Implement LFSR functionality for q[4]
      q[2] <= q[0] ^ q[3]; // Implement LFSR functionality for q[2] with tap at position 3
      q[3] <= q[4];        // Shift functionality for q[3]
      q[1] <= q[2];        // Shift functionality for q[1]
      q[0] <= q[1];        // Shift functionality for q[0]
    end
  end

endmodule