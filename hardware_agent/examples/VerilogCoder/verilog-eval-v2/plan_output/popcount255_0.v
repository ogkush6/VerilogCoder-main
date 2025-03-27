module TopModule
(
  input  logic [254:0] in,
  output logic [7:0]   out
);

  // Combinational logic

  always @(*) begin
    out = 0;
    for (int i = 0; i < 255; i = i + 1) begin
      out = out + in[i];
    end
  end

endmodule