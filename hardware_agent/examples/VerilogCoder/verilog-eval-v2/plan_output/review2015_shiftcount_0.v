module TopModule
(
  input  logic clk,
  input  logic shift_ena,
  input  logic count_ena,
  input  logic data,
  output logic [3:0] q
);

  // 4-bit register to hold the current value of the shift register/counter
  logic [3:0] reg_q;

  // Initialize the register to a known value at the start
  initial begin
    reg_q = 4'b0000;
  end

  // Sequential logic for shifting data into the register
  always @(posedge clk) begin
    if (shift_ena) begin
      reg_q <= {reg_q[2:0], data}; // Shift data into LSB, shift other bits left
    end
    else if (count_ena) begin
      reg_q <= reg_q - 1; // Decrement the value in the register
    end
  end

  // Structural connections
  assign q = reg_q;

endmodule