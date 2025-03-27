module TopModule
(
  input  logic       clk,
  input  logic       reset,
  input  logic [7:0] d,
  output logic [7:0] q
);

  // D flip-flop for the least significant bit
  always @(posedge clk) begin
    if (reset)
      q[0] <= 0;
    else
      q[0] <= d[0];
  end

  // D flip-flop for the second bit
  always @(posedge clk) begin
    if (reset)
      q[1] <= 0;
    else
      q[1] <= d[1];
  end

  // D flip-flop for the third bit
  always @(posedge clk) begin
    if (reset)
      q[2] <= 0;
    else
      q[2] <= d[2];
  end

  // D flip-flop for the fourth bit
  always @(posedge clk) begin
    if (reset)
      q[3] <= 0;
    else
      q[3] <= d[3];
  end

  // D flip-flop for the fifth bit
  always @(posedge clk) begin
    if (reset)
      q[4] <= 0;
    else
      q[4] <= d[4];
  end

  // D flip-flop for the sixth bit
  always @(posedge clk) begin
    if (reset)
      q[5] <= 0;
    else
      q[5] <= d[5];
  end

  // D flip-flop for the seventh bit
  always @(posedge clk) begin
    if (reset)
      q[6] <= 0;
    else
      q[6] <= d[6];
  end

  // D flip-flop for the eighth bit
  always @(posedge clk) begin
    if (reset)
      q[7] <= 0;
    else
      q[7] <= d[7];
  end

endmodule