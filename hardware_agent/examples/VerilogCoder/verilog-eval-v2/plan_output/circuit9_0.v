module TopModule
(
  input  logic clk,
  input  logic a,
  output logic [2:0] q
);

  // 3-bit register for output 'q'
  logic [2:0] q_reg;

  always @(posedge clk) begin
    if (a)
      q_reg <= 3'b100; // Set 'q' to 4 when 'a' is high during the first clock cycle
    else if (!a) begin
      if (q_reg == 3'b110) // When 'q' reaches 6
        q_reg <= 3'b000; // Reset 'q' to 0
      else
        q_reg <= q_reg + 1; // Increment 'q' by 1 when 'a' is low
    end
  end

  assign q = q_reg;

endmodule