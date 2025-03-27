module TopModule
(
  input  logic [2:0] in,
  output logic [1:0] out
);

  // Define a 2-bit register to store the count of '1's in the input vector
  logic [1:0] count;

  // Combinational logic to count the number of '1's in the 3-bit input vector
  always @(*) begin
    case (in)
      3'b000: count = 2'b00;
      3'b001: count = 2'b01;
      3'b010: count = 2'b01;
      3'b011: count = 2'b10;
      3'b100: count = 2'b01;
      3'b101: count = 2'b10;
      3'b110: count = 2'b10;
      3'b111: count = 2'b11;
    endcase
  end

  // Assign the output to the count
  assign out = count;

endmodule