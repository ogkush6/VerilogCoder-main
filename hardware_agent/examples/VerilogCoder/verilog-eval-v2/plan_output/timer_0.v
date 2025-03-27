module TopModule
(
  input  logic       clk,
  input  logic       load,
  input  logic [9:0] data,
  output logic       tc
);

  // 10-bit register to hold the countdown value
  logic [9:0] counter;

  always @( posedge clk ) begin
    if ( load )
      counter <= data;
    else if (counter > 0)
      counter <= counter - 1;
    else
      counter <= 0;
  end

  // Implement a signal 'tc' that is asserted (set to 1) when the countdown register reaches 0.
  // This signal should be deasserted (set to 0) when the countdown register is greater than 0.
  assign tc = (counter == 0) ? 1'b1 : 1'b0;

endmodule