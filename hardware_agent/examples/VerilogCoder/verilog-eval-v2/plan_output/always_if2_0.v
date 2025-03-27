module TopModule (
    input      logic cpu_overheated,
    output reg shut_off_computer,
    input      logic arrived,
    input      logic gas_tank_empty,
    output reg keep_driving
);

    always @(*) begin
        shut_off_computer = cpu_overheated ? 1 : 0;
    end

    always @(*) begin
        keep_driving = (~arrived & ~gas_tank_empty) ? 1 : 0;
    end

endmodule