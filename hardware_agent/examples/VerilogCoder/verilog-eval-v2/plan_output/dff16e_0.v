module TopModule
(
  input  logic       clk,
  input  logic       resetn,
  input  logic [1:0] byteena,
  input  logic [15:0] d,
  output logic [15:0] q
);

  // Sequential logic

  always @( posedge clk ) begin
    if ( ~resetn )
      q <= 16'b0;
    else begin
      if ( byteena[1] )
        q[15:8] <= d[15:8];
      if ( byteena[0] )
        q[7:0] <= d[7:0];
    end
  end

endmodule