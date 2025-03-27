module TopModule
(
  input  logic       clk,
  input  logic       areset,
  input  logic [7:0] d,
  output logic [7:0] q
);

  // Sequential logic
  logic [7:0] q_reg;

  genvar i;
  generate
    for (i = 0; i < 8; i = i + 1) begin : dff
      always @( posedge clk or posedge areset ) begin
        if ( areset )
          q_reg[i] <= 1'b0;
        else
          q_reg[i] <= d[i];
      end
    end
  endgenerate

  assign q = q_reg;

endmodule