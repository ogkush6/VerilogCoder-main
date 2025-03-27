module TopModule
(
  input  logic       clk,
  input  logic       areset,
  input  logic       load,
  input  logic       ena,
  input  logic [3:0] data,
  output logic [3:0] q
);

  // Shift register
  logic [3:0] shift_reg;

  // Asynchronous reset logic
  always @(posedge clk or posedge areset) begin
    if (areset)
      shift_reg <= 4'b0000;
    else if (load)
      shift_reg <= data; // Load data into shift register when load is high
    else if (ena)
      shift_reg <= {1'b0, shift_reg[3:1]}; // Shift right when ena is high and load is low
    else
      shift_reg <= shift_reg; // No operation when areset, load and ena are not asserted
  end

  assign q = shift_reg;

endmodule