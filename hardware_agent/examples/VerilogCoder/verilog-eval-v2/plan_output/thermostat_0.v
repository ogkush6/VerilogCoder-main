module TopModule
(
  input  logic mode,
  input  logic too_cold,
  input  logic too_hot,
  input  logic fan_on,
  output logic heater,
  output logic aircon,
  output logic fan
);

  // Combinational logic for heater control
  always @(*) begin
    heater = (mode && too_cold) ? 1'b1 : 1'b0;
  end

  // Combinational logic for air conditioner control
  always @(*) begin
    aircon = (!mode && too_hot) ? 1'b1 : 1'b0;
  end

  // Combinational logic for fan control
  always @(*) begin
    fan = (heater || aircon || fan_on) ? 1'b1 : 1'b0;
  end

endmodule