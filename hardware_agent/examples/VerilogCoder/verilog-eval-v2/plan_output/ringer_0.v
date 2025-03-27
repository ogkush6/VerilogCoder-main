module TopModule
(
  input  logic ring,
  input  logic vibrate_mode,
  output logic ringer,
  output logic motor
);

  // Combinational logic for ringer output
  always @(*) begin
    if (ring && !vibrate_mode)
      ringer = 1'b1;
    else
      ringer = 1'b0;
  end

  // Combinational logic for motor output
  always @(*) begin
    if (ring && vibrate_mode)
      motor = 1'b1;
    else
      motor = 1'b0;
  end

endmodule