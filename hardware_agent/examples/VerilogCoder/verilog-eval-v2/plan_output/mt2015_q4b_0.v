module TopModule
(
  input  logic x,
  input  logic y,
  output logic z
);

  // Combinational logic for z
  always @(*) begin
    if ((x == 1'b0) && (y == 1'b0)) 
      z = 1'b1;
    else if ((x == 1'b1) && (y == 1'b1)) 
      z = 1'b1;
    else 
      z = 1'b0;
  end
endmodule