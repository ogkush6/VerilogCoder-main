module TopModule
(
  input  logic [3:0] x,
  input  logic [3:0] y,
  output logic [4:0] sum
);

  // Full adder for LSB
  logic carry_out0, carry_out1, carry_out2, carry_out3;
  
  initial begin
    carry_out0 = 0;
  end
  
  always @(*) begin
    sum[0] = x[0] ^ y[0] ^ carry_out0;
    carry_out1 = (x[0] & y[0]) | (carry_out0 & (x[0] ^ y[0]));
  end

  // Full adder for second LSB
  always @(*) begin
    sum[1] = x[1] ^ y[1] ^ carry_out1;
    carry_out2 = (x[1] & y[1]) | (carry_out1 & (x[1] ^ y[1]));
  end

  // Full adder for third LSB
  always @(*) begin
    sum[2] = x[2] ^ y[2] ^ carry_out2;
    carry_out3 = (x[2] & y[2]) | (carry_out2 & (x[2] ^ y[2]));
  end

  // Full adder for MSB
  always @(*) begin
    sum[3] = x[3] ^ y[3] ^ carry_out3;
    carry_out3 = (x[3] & y[3]) | (carry_out3 & (x[3] ^ y[3]));
  end

  // Final carry-out bit
  assign sum[4] = carry_out3;

endmodule