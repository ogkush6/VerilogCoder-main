module TopModule
(
  input  logic c,
  input  logic d,
  output logic [3:0] mux_in
);

  // Combinational logic for mux_in[0]
  always @(*) begin
    mux_in[0] = (c & ~d) | (~c & d) | (c & d);  // Covering cases 0,1; 1,1; 1,0
  end

  // Combinational logic for mux_in[1]
  assign mux_in[1] = 1'b0;  // Always 0

  // Combinational logic for mux_in[2]
  always @(*) begin
    mux_in[2] = (~c & ~d) | (c & ~d);  // Covering cases 0,0; 1,0
  end

  // Combinational logic for mux_in[3]
  always @(*) begin
    mux_in[3] = (c & d);  // Covering case 1,1
  end

endmodule