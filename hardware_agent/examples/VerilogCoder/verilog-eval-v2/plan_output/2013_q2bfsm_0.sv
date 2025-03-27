`timescale 1 ps/1 ps
`define OK 12
`define INCORRECT 13


module stimulus_gen (
	input clk,
	output logic resetn,
	output logic x, y
);

	initial begin
		resetn = 0;
		x = 0;
		y = 0;
		@(posedge clk);
		@(posedge clk);
		resetn = 1;
		repeat(500) @(negedge clk) begin
			resetn <= ($random & 31) != 0;
			{x,y} <= $random;
		end
		
		#1 $finish;
	end
	
endmodule

module tb();

	typedef struct packed {
		int errors;
		int errortime;
		int errors_f;
		int errortime_f;
		int errors_g;
		int errortime_g;

		int clocks;
	} stats;
	
	stats stats1;
	
	
	wire[511:0] wavedrom_title;
	wire wavedrom_enable;
	int wavedrom_hide_after_time;
	
	reg clk=0;
	initial forever
		#5 clk = ~clk;

	logic resetn;
	logic x;
	logic y;
	logic f_ref;
	logic f_dut;
	logic g_ref;
	logic g_dut;

	initial begin 
		$dumpfile("wave.vcd");
		$dumpvars();
	end


	wire tb_match;		// Verification
	wire tb_mismatch = ~tb_match;
	
	stimulus_gen stim1 (
		.clk,
		.* ,
		.resetn,
		.x,
		.y );
	RefModule good1 (
		.clk,
		.resetn,
		.x,
		.y,
		.f(f_ref),
		.g(g_ref) );
		
	TopModule top_module1 (
		.clk,
		.resetn,
		.x,
		.y,
		.f(f_dut),
		.g(g_dut) );

	
	bit strobe = 0;
	task wait_for_end_of_timestep;
		repeat(5) begin
			strobe <= !strobe;  // Try to delay until the very end of the time step.
			@(strobe);
		end
	endtask	

	
	final begin
		if (stats1.errors_f) $display("Hint: Output '%s' has %0d mismatches. First mismatch occurred at time %0d.", "f", stats1.errors_f, stats1.errortime_f);
		else $display("Hint: Output '%s' has no mismatches.", "f");
		if (stats1.errors_g) $display("Hint: Output '%s' has %0d mismatches. First mismatch occurred at time %0d.", "g", stats1.errors_g, stats1.errortime_g);
		else $display("Hint: Output '%s' has no mismatches.", "g");

		$display("Hint: Total mismatched samples is %1d out of %1d samples\n", stats1.errors, stats1.clocks);
		$display("Simulation finished at %0d ps", $time);
		$display("Mismatches: %1d in %1d samples", stats1.errors, stats1.clocks);
	end
	
	// Verification: XORs on the right makes any X in good_vector match anything, but X in dut_vector will only match X.
	assign tb_match = ( { f_ref, g_ref } === ( { f_ref, g_ref } ^ { f_dut, g_dut } ^ { f_ref, g_ref } ) );
	// Use explicit sensitivity list here. @(*) causes NetProc::nex_input() to be called when trying to compute
	// the sensitivity list of the @(strobe) process, which isn't implemented.
	always @(posedge clk, negedge clk) begin

		stats1.clocks++;
		if (!tb_match) begin
			if (stats1.errors == 0) stats1.errortime = $time;
			stats1.errors++;
		end
		if (f_ref !== ( f_ref ^ f_dut ^ f_ref ))
		begin if (stats1.errors_f == 0) stats1.errortime_f = $time;
			stats1.errors_f = stats1.errors_f+1'b1; end
		if (g_ref !== ( g_ref ^ g_dut ^ g_ref ))
		begin if (stats1.errors_g == 0) stats1.errortime_g = $time;
			stats1.errors_g = stats1.errors_g+1'b1; end

	end

   // add timeout after 100K cycles
   initial begin
     #1000000
     $display("TIMEOUT");
     $finish();
   end

endmodule



module RefModule (
  input clk,
  input resetn,
  input x,
  input y,
  output f,
  output g
);

  parameter A=0, B=1, S0=2, S1=3, S10=4, G1=5, G2=6, P0=7, P1=8;
  reg [3:0] state, next;

  always @(posedge clk) begin
    if (~resetn) state <= A;
    else state <= next;
  end

  always_comb begin
    case (state)
      A: next = B;
      B: next = S0;
      S0: next = x ? S1 : S0;
      S1: next = x ? S1 : S10;
      S10: next = x? G1 : S0;
      G1: next = y ? P1 : G2;
      G2: next = y ? P1 : P0;
      P0: next = P0;
      P1: next = P1;
      default: next = 'x;
    endcase
  end

  assign f = (state == B);
  assign g = (state == G1) || (state == G2) || (state == P1);

endmodule


module TopModule (
    input  logic clk,
    input  logic resetn,
    input  logic x,
    input  logic y,
    output logic f,
    output logic g
);

    // State identifiers
    localparam STATE_A = 3'b000;  // Initial state
    localparam STATE_B = 3'b001;  // Set f to 1 for one cycle
    localparam STATE_C = 3'b010;  // Monitor x for first 1
    localparam STATE_D = 3'b011;  // Monitor x for following 0
    localparam STATE_E = 3'b100;  // Monitor x for last 1
    localparam STATE_F = 3'b101;  // Set g to 1 and monitor y in first cycle
    localparam STATE_G = 3'b110;  // Monitor y in second cycle
    localparam STATE_H = 3'b111;  // Maintain g = 1 forever
    localparam STATE_I = 4'b1000; // Set g = 0 forever

    // State register
    logic [3:0] state;
    logic [3:0] state_next;

    // State transition logic
    always @(posedge clk) begin
        if (!resetn) begin
            state <= STATE_A;
        end else begin
            state <= state_next;
        end
    end

    // Next state logic
    always @(*) begin
        state_next = state; // Default to stay in the current state
        case (state)
            STATE_A: begin
                state_next = STATE_B;
            end
            STATE_B: begin
                state_next = STATE_C;
            end
            STATE_C: begin
                if (x == 1) begin
                    state_next = STATE_D;
                end
            end
            STATE_D: begin
                if (x == 0) begin
                    state_next = STATE_E;
                end
            end
            STATE_E: begin
                if (x == 1) begin
                    state_next = STATE_F;
                end else begin
                    state_next = STATE_C; // Go back to monitor first x=1
                end
            end
            STATE_F: begin
                if (y == 1) begin
                    state_next = STATE_H;
                end else begin
                    state_next = STATE_G;
                end
            end
            STATE_G: begin
                if (y == 1) begin
                    state_next = STATE_H;
                end else begin
                    state_next = STATE_I;
                end
            end
            STATE_H: begin
                // Maintain g = 1 forever
                state_next = STATE_H;
            end
            STATE_I: begin
                // Maintain g = 0 forever
                state_next = STATE_I;
            end
            default: begin
                state_next = STATE_A;
            end
        endcase
    end

    // Output logic
    always @(*) begin
        f = 0; // Default value for f
        g = 0; // Default value for g

        case (state)
            STATE_B: begin
                f = 1; // Set f to 1 for one cycle
            end
            STATE_F: begin
                g = 1; // Set g to 1 when entering STATE_F
            end
            STATE_G: begin
                g = 1; // Keep g at 1 during STATE_G
            end
            STATE_H: begin
                g = 1; // Maintain g = 1 forever
            end
            STATE_I: begin
                g = 0; // Maintain g = 0 forever
            end
        endcase
    end

endmodule