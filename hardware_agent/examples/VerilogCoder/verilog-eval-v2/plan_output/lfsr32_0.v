module TopModule (
  input  logic clk,
  input  logic reset,
  output logic [31:0] q
);

  always @(posedge clk) begin
    if (reset) begin
      q <= 32'h1;
    end else begin
      // Correctly handle the LFSR taps and wrapping of the MSB
      q[31] <= q[0]; // MSB is the wrap-around of LSB
      q[30:22] <= q[31:23]; // Shift the bits between tap positions
      q[21] <= q[22] ^ q[0]; // Tap at position 22
      q[20:2] <= q[21:3]; // Shift the bits between tap positions
      q[1] <= q[2] ^ q[0]; // Tap at position 2
      q[0] <= q[1] ^ q[0]; // Tap at position 1
    end
  end

endmodule