module TopModule
(
  input  logic       clk,
  input  logic       areset,
  input  logic       predict_valid,
  input  logic       predict_taken,
  input  logic       train_mispredicted,
  input  logic       train_taken,
  input  logic [31:0] train_history,
  output logic [31:0] predict_history
);

  // 32-bit global history shift register
  logic [31:0] history_reg;

  // Asynchronous reset
  always @(posedge clk or posedge areset) begin
    if (areset)
      history_reg <= 32'b0;
    else if (train_mispredicted)
      history_reg <= {train_history[30:0], train_taken};
    else if (predict_valid && !train_mispredicted)
      history_reg <= {history_reg[30:0], predict_taken};
  end

  assign predict_history = history_reg;
endmodule