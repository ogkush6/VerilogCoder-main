module TopModule
(
  input  logic       clk,
  input  logic       load,
  input  logic [511:0] data,
  output logic [511:0] q
);

  logic [511:0] next_q;

  // 512-bit register to hold the state of the cellular automaton
  always @(posedge clk) begin
    if (load) begin
      q <= data;
    end else begin
      q <= next_q;
    end
  end

  // Combinational logic for Rule 110
  always @(*) begin
    for (int i = 0; i < 512; i++) begin
      logic left, center, right;
      center = q[i];
      if (i == 0) begin
        right = 0; // Boundary condition
        left = q[i+1];
      end else if (i == 511) begin
        left = 0; // Boundary condition
        right = q[i-1];
      end else begin
        left = q[i+1];
        right = q[i-1];
      end

      // Rule 110 logic
      case ({left, center, right})
        3'b111: next_q[i] = 1'b0;
        3'b110: next_q[i] = 1'b1;
        3'b101: next_q[i] = 1'b1;
        3'b100: next_q[i] = 1'b0;
        3'b011: next_q[i] = 1'b1;
        3'b010: next_q[i] = 1'b1;
        3'b001: next_q[i] = 1'b1;
        3'b000: next_q[i] = 1'b0;
      endcase
    end
  end

endmodule