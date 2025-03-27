module TopModule
(
  input  logic       clk,
  input  logic       load,
  input  logic       ena,
  input  logic [1:0] amount,
  input  logic [63:0] data,
  output logic [63:0] q
);

  // 64-bit register to hold the value of the shift register
  logic [63:0] shift_reg;

  always @( posedge clk ) begin
    if ( load )
      shift_reg <= data;
    else if ( ena )
      case ( amount )
        2'b00: shift_reg <= shift_reg << 1; // Shift left by 1 bit when ena is high and amount is 2'b00
        2'b01: shift_reg <= shift_reg << 8; // Shift left by 8 bits when ena is high and amount is 2'b01
        2'b10: shift_reg <= $signed(shift_reg) >>> 1; // Arithmetic shift right by 1 bit when ena is high and amount is 2'b10
        2'b11: shift_reg <= $signed(shift_reg) >>> 8; // Arithmetic shift right by 8 bits when ena is high and amount is 2'b11
      endcase
  end

  assign q = shift_reg;

endmodule