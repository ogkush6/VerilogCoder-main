module TopModule
(
  input  logic       clk,
  input  logic       load,
  input  logic [1:0] ena,
  input  logic [99:0] data,
  output logic [99:0] q
);

  // 100-bit register to store the current state of the rotator
  logic [99:0] rotator_reg;

  always @( posedge clk ) begin
    if ( load )
      rotator_reg <= data;
    else if ( ena == 2'b01 ) // rotate right
      rotator_reg <= {rotator_reg[0], rotator_reg[99:1]};
    else if ( ena == 2'b10 ) // rotate left
      rotator_reg <= {rotator_reg[98:0], rotator_reg[99]};
    else if ( ena == 2'b00 || ena == 2'b11 ) // do not rotate
      rotator_reg <= rotator_reg;
  end

  assign q = rotator_reg;

endmodule