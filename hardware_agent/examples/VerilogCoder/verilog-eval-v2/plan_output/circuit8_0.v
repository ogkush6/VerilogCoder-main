module TopModule(
    input logic clock,
    input logic a,
    output logic p,
    output logic q
);

    // Latch for output p that is transparent when 'clock' is high
    always @(*) begin
        if (clock) begin
            p = a;
        end
    end

    // Latch for output q
    always @(negedge clock) begin
        q <= p;
    end

endmodule