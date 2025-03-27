module TopModule
(
  input  logic       clk,
  input  logic [7:0] d,
  output logic [7:0] q
);

  // Initialize q to 0
  initial begin
    q <= 8'b0;
  end

  // D flip-flop for d[0] and q[0]
  always @(posedge clk) begin
    q[0] <= d[0];
  end

  // D flip-flop for d[1] and q[1]
  always @(posedge clk) begin
    q[1] <= d[1];
  end

  // D flip-flop for d[2] and q[2]
  always @(posedge clk) begin
    q[2] <= d[2];
  end

  // D flip-flop for d[3] and q[3]
  always @(posedge clk) begin
    q[3] <= d[3];
  end

  // D flip-flop for d[4] and q[4]
  always @(posedge clk) begin
    q[4] <= d[4];
  end

  // D flip-flop for d[5] and q[5]
  always @(posedge clk) begin
    q[5] <= d[5];
  end

  // D flip-flop for d[6] and q[6]
  always @(posedge clk) begin
    q[6] <= d[6];
  end

  // D flip-flop for d[7] and q[7]
  always @(posedge clk) begin
    q[7] <= d[7];
  end

endmodule