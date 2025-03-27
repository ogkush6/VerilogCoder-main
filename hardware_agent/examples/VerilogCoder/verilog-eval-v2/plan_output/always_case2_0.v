module TopModule
(
  input  logic [3:0] in,
  output logic [1:0] pos
);

  // Combinational logic

  always @(*) begin
    if (in[0])
      pos = 2'b00;
    else if (in[1])
      pos = 2'b01;
    else if (in[2])
      pos = 2'b10;
    else if (in[3])
      pos = 2'b11;
    else
      pos = 2'b00;
  end

endmodule