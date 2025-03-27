module TopModule
(
  input  logic [1023:0] in,
  input  logic [7:0]    sel,
  output logic [3:0]    out
);

  // Wire to hold the selected bits
  logic [3:0] selected_bits;

  // Multiplexer logic
  always @(*) begin
    selected_bits = in[sel*4 +: 4];
  end

  // Assign selected bits to output
  assign out = selected_bits;

endmodule