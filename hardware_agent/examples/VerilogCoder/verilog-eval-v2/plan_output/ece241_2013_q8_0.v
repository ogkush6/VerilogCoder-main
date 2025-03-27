module TopModule
(
  input  logic clk,
  input  logic aresetn,
  input  logic x,
  output logic z
);

  // State encoding
  localparam S0 = 2'b00;
  localparam S1 = 2'b01;
  localparam S2 = 2'b10;

  // State register
  logic [1:0] state;

  always @(posedge clk or negedge aresetn) begin
    if (!aresetn) begin
      state <= S0;
    end else begin
      case (state)
        S0: state <= (x) ? S1 : S0;
        S1: state <= (x) ? S1 : S2;
        S2: state <= (x) ? S1 : S0;
      endcase
    end
  end

  // Output logic for z
  always @(*) begin
    if (state == S2 && x == 1'b1) begin
      z = 1'b1;
    end else begin
      z = 1'b0;
    end
  end

endmodule